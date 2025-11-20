import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import google.generativeai as genai
import math

# Page config
st.set_page_config(
    page_title="Hệ thống Cứu hộ SOS",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default Gemini API Key
DEFAULT_GEMINI_API_KEY = "AIzaSyCRMXgg-HuKvJdi0hKuen94oUR3MPsQBFQ"

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = DEFAULT_GEMINI_API_KEY

# Load data
@st.cache_data
def load_data():
    csv_file = "mở quyền sửa đổi - HOÀN THIỆN - KV.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Clean column names
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame()

def save_data(df):
    csv_file = "mở quyền sửa đổi - HOÀN THIỆN - KV.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    st.cache_data.clear()

def analyze_address_with_gemini(address, api_key):
    """Sử dụng Gemini API để phân tích và làm rõ địa chỉ"""
    if not api_key:
        return address, "Vui lòng nhập API key Gemini"
    
    try:
        genai.configure(api_key=api_key)
        # Sử dụng gemini-2.5-flash - model mới nhất và nhanh nhất
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Phân tích và làm rõ địa chỉ sau đây, trả về địa chỉ đã được chuẩn hóa và rõ ràng hơn. 
        Nếu địa chỉ đã rõ ràng thì giữ nguyên. Chỉ trả về địa chỉ đã được cải thiện, không thêm giải thích.
        
        Địa chỉ gốc: {address}
        
        Địa chỉ đã được chuẩn hóa:"""
        
        response = model.generate_content(prompt)
        improved_address = response.text.strip()
        
        # Kiểm tra nếu địa chỉ được cải thiện có vẻ hợp lý
        if improved_address and len(improved_address) > 5:
            return improved_address, "Thành công"
        else:
            return address, "Địa chỉ không được cải thiện"
    except Exception as e:
        error_msg = str(e)
        # Kiểm tra lỗi quota
        if "429" in error_msg or "quota" in error_msg.lower() or "Quota exceeded" in error_msg:
            return address, "Quota API đã hết. Sử dụng địa chỉ gốc."
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            return address, "API key không hợp lệ."
        else:
            return address, f"Lỗi: {error_msg[:100]}"

def extract_area_from_address(address, api_key):
    """Sử dụng Gemini API để trích xuất khu vực từ địa chỉ"""
    if not api_key:
        return "", "Vui lòng nhập API key Gemini"
    
    try:
        genai.configure(api_key=api_key)
        # Sử dụng gemini-2.5-flash - model mới nhất và nhanh nhất
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Từ địa chỉ sau đây, hãy trích xuất tên khu vực/địa danh chính (ví dụ: Diên Khánh, Diên Lạc, Diên An, Cầu Bè, Bàn Thạch, v.v.).
        Chỉ trả về tên khu vực, không thêm giải thích hay từ ngữ khác.
        Nếu không tìm thấy khu vực rõ ràng, trả về "Khác".
        
        Địa chỉ: {address}
        
        Khu vực:"""
        
        response = model.generate_content(prompt)
        area = response.text.strip()
        
        # Làm sạch kết quả
        area = area.replace("Khu vực:", "").replace("khu vực:", "").strip()
        if not area or len(area) < 2:
            area = "Khác"
        
        return area, "Thành công"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "Quota exceeded" in error_msg:
            return "Khác", "Quota API đã hết"
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            return "Khác", "API key không hợp lệ"
        else:
            return "Khác", f"Lỗi: {error_msg[:100]}"

def geocode_address(address, api_key):
    """Sử dụng Gemini API để geocode địa chỉ thành tọa độ lat/long"""
    if not api_key:
        return None, None, "Vui lòng nhập API key Gemini"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Từ địa chỉ sau đây ở Việt Nam, hãy trả về tọa độ địa lý (latitude, longitude) dạng số thập phân.
        Chỉ trả về 2 số cách nhau bởi dấu phẩy, không có chữ hay ký tự khác.
        Ví dụ: 12.2388, 109.1967
        
        Địa chỉ: {address}
        
        Tọa độ (lat, lng):"""
        
        response = model.generate_content(prompt)
        coords = response.text.strip()
        
        # Parse coordinates
        try:
            # Làm sạch kết quả
            coords = coords.replace("(", "").replace(")", "").replace("Tọa độ:", "").replace("lat, lng:", "").strip()
            parts = coords.split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                # Kiểm tra tọa độ hợp lệ cho Việt Nam (khoảng 8-24N, 102-110E)
                if 8 <= lat <= 24 and 102 <= lng <= 110:
                    return lat, lng, "Thành công"
        except:
            pass
        
        return None, None, "Không thể parse tọa độ"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "Quota exceeded" in error_msg:
            return None, None, "Quota API đã hết"
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            return None, None, "API key không hợp lệ"
        else:
            return None, None, f"Lỗi: {error_msg[:100]}"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 điểm (Haversine formula) - trả về km"""
    R = 6371  # Bán kính Trái Đất (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

# Load data
if st.session_state.data is None:
    st.session_state.data = load_data()
    st.session_state.original_data = st.session_state.data.copy()

# Sidebar
with st.sidebar:
    st.title("🚨 Hệ thống Cứu hộ SOS")
    st.markdown("---")
    
    # Gemini API Key
    st.subheader("⚙️ Cấu hình")
    api_key = st.text_input(
        "Gemini API Key (Tùy chọn)",
        value=st.session_state.gemini_api_key if st.session_state.gemini_api_key != DEFAULT_GEMINI_API_KEY else "",
        type="password",
        help="API key mặc định đã được cấu hình. Nhập key khác nếu muốn thay đổi."
    )
    # Use default key if user hasn't entered one, otherwise use user's key
    st.session_state.gemini_api_key = api_key if api_key else DEFAULT_GEMINI_API_KEY
    
    st.markdown("---")
    
    # Statistics
    if not st.session_state.data.empty:
        st.subheader("📊 Thống kê")
        total_cases = len(st.session_state.data)
        urgent_cases = len(st.session_state.data[st.session_state.data['Mức độ ưu tiên'] == 'Khẩn cấp'])
        st.metric("Tổng số trường hợp", total_cases)
        st.metric("Trường hợp khẩn cấp", urgent_cases)
        
        # Area statistics
        if 'Chi tiết khu vực' in st.session_state.data.columns:
            area_counts = st.session_state.data['Chi tiết khu vực'].value_counts().head(10)
            st.markdown("**Top 10 khu vực:**")
            for area, count in area_counts.items():
                st.text(f"{area}: {count}")

# Main content
st.title("🚨 Hệ thống Quản lý Yêu cầu Cứu hộ")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Tìm kiếm & Lọc", "➕ Thêm yêu cầu mới", "📊 Phân tích địa chỉ"])

with tab1:
    st.header("Tìm kiếm và Lọc dữ liệu")
    
    if st.session_state.data.empty:
        st.warning("Không có dữ liệu. Vui lòng kiểm tra file CSV.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Priority filter
            if 'Mức độ ưu tiên' in st.session_state.data.columns:
                priorities = ['Tất cả'] + sorted(st.session_state.data['Mức độ ưu tiên'].dropna().unique().tolist())
                selected_priority = st.selectbox("Mức độ ưu tiên", priorities)
            else:
                selected_priority = 'Tất cả'
        
        with col2:
            # Area filter
            if 'Chi tiết khu vực' in st.session_state.data.columns:
                areas = ['Tất cả'] + sorted(st.session_state.data['Chi tiết khu vực'].dropna().unique().tolist())
                selected_area = st.selectbox("Khu vực", areas)
            else:
                selected_area = 'Tất cả'
        
        with col3:
            # Search by address
            search_term = st.text_input("Tìm kiếm theo địa chỉ", "")
        
        # Apply filters
        filtered_data = st.session_state.original_data.copy()
        
        if selected_priority != 'Tất cả' and 'Mức độ ưu tiên' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Mức độ ưu tiên'] == selected_priority]
        
        if selected_area != 'Tất cả' and 'Chi tiết khu vực' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Chi tiết khu vực'] == selected_area]
        
        if search_term:
            if 'Địa chỉ' in filtered_data.columns:
                filtered_data = filtered_data[
                    filtered_data['Địa chỉ'].astype(str).str.contains(search_term, case=False, na=False)
                ]
        
        # Display results
        st.markdown(f"**Tìm thấy {len(filtered_data)} kết quả**")
        
        if not filtered_data.empty:
            # Display options
            display_col1, display_col2 = st.columns([3, 1])
            with display_col1:
                show_all = st.checkbox("Hiển thị tất cả", value=False)
            with display_col2:
                items_per_page = st.selectbox("Số dòng mỗi trang", [10, 25, 50, 100], index=1)
            
            # Pagination
            if not show_all:
                total_pages = (len(filtered_data) - 1) // items_per_page + 1
                page = st.number_input("Trang", min_value=1, max_value=total_pages, value=1)
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                display_data = filtered_data.iloc[start_idx:end_idx]
                st.caption(f"Hiển thị {start_idx + 1}-{min(end_idx, len(filtered_data))} / {len(filtered_data)}")
            else:
                display_data = filtered_data
            
            # Display table
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Download filtered data
            csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Tải xuống dữ liệu đã lọc",
                data=csv,
                file_name=f"cuu_ho_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Không tìm thấy kết quả nào phù hợp với bộ lọc.")

with tab2:
    st.header("Thêm yêu cầu cứu hộ mới")
    
    # Initialize GPS coordinates in session state
    if 'gps_coords' not in st.session_state:
        st.session_state.gps_coords = ""
    
    # GPS location button outside form
    col_gps1, col_gps2 = st.columns([3, 1])
    with col_gps1:
        st.markdown("**Lấy vị trí GPS:**")
    with col_gps2:
        get_gps_clicked = st.button("📍 Lấy vị trí GPS", help="Lấy tọa độ GPS của bạn", use_container_width=True)
    
    if get_gps_clicked:
        st.markdown("""
        <div id="gps-location-result" style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px;"></div>
        <script>
        function getGPSLocation() {
            const resultDiv = document.getElementById('gps-location-result');
            if (navigator.geolocation) {
                resultDiv.innerHTML = '<p style="color: blue;">⏳ Đang lấy vị trí...</p>';
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const coords = lat.toFixed(6) + ',' + lng.toFixed(6);
                        resultDiv.innerHTML = '<p style="color: green;"><strong>✅ Vị trí của bạn:</strong><br>' + 
                            coords + '</p><p style="color: blue;">✓ Đã copy vào clipboard! Vui lòng dán vào ô địa chỉ bên dưới.</p>';
                        
                        // Copy to clipboard
                        navigator.clipboard.writeText(coords).then(() => {
                            console.log('Coordinates copied to clipboard');
                        });
                    },
                    function(error) {
                        resultDiv.innerHTML = '<p style="color: red;">❌ Lỗi: ' + error.message + '</p>';
                    }
                );
            } else {
                resultDiv.innerHTML = '<p style="color: red;">❌ Trình duyệt không hỗ trợ Geolocation API</p>';
            }
        }
        getGPSLocation();
        </script>
        """, unsafe_allow_html=True)
    
    with st.form("add_rescue_request", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox(
                "Mức độ ưu tiên *",
                ["Khẩn cấp", "Cao", "Trung bình", "Thấp"],
                index=0
            )
            
            num_people = st.text_input("Số người", placeholder="VD: 5, Nhiều, 10-15")
        
        with col2:
            address = st.text_area(
                "Địa chỉ *", 
                height=100, 
                placeholder="Nhập địa chỉ chi tiết hoặc tọa độ (lat,lng)...\nVí dụ: 12.2388,109.1967",
                value=st.session_state.gps_coords if st.session_state.gps_coords else ""
            )
            
            phone = st.text_input("Số điện thoại", placeholder="VD: 0912345678, 0901234567")
        
        st.info("ℹ️ AI sẽ tự động phân tích địa chỉ để: cải thiện địa chỉ và trích xuất khu vực.")
        
        submitted = st.form_submit_button("➕ Thêm yêu cầu", type="primary")
        
        if submitted:
            # Validation
            if not address:
                st.error("Vui lòng điền địa chỉ (*)")
            else:
                # Automatically improve address and extract area with Gemini
                final_address = address
                extracted_area = "Khác"
                
                if st.session_state.gemini_api_key:
                    with st.spinner("🔄 Đang phân tích địa chỉ với AI (cải thiện địa chỉ và trích xuất khu vực)..."):
                        # Cải thiện địa chỉ
                        final_address, address_status = analyze_address_with_gemini(address, st.session_state.gemini_api_key)
                        if "Quota" in address_status or "quota" in address_status.lower():
                            st.warning("⚠️ Quota API đã hết. Sử dụng địa chỉ gốc. Vui lòng thử lại sau hoặc kiểm tra billing.")
                            final_address = address
                        elif "Lỗi" in address_status or "Vui lòng" in address_status or "không hợp lệ" in address_status.lower():
                            st.warning(f"⚠️ {address_status}. Sử dụng địa chỉ gốc.")
                            final_address = address
                        elif address_status == "Thành công" and final_address != address:
                            st.success("✅ Đã tự động cải thiện địa chỉ!")
                            st.info(f"**Địa chỉ gốc:** {address}\n\n**Địa chỉ đã cải thiện:** {final_address}")
                        else:
                            final_address = address
                        
                        # Trích xuất khu vực từ địa chỉ đã cải thiện
                        extracted_area, area_status = extract_area_from_address(final_address, st.session_state.gemini_api_key)
                        if area_status == "Thành công":
                            st.success(f"✅ Đã tự động trích xuất khu vực: **{extracted_area}**")
                        elif "Quota" in area_status:
                            st.warning("⚠️ Không thể trích xuất khu vực do hết quota. Sử dụng 'Khác'.")
                        else:
                            st.warning(f"⚠️ Không thể trích xuất khu vực. Sử dụng 'Khác'.")
                else:
                    st.warning("⚠️ Chưa có API key. Khu vực sẽ được đặt là 'Khác'.")
                
                # Create new row
                new_row = pd.DataFrame({
                    'Mức độ ưu tiên': [priority],
                    'Chi tiết khu vực': [extracted_area],
                    'Số người': [num_people if num_people else ""],
                    'Địa chỉ': [final_address],
                    'Số điện thoại': [phone if phone else ""]
                })
                
                # Add to data
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.session_state.original_data = st.session_state.data.copy()
                
                # Save to CSV
                save_data(st.session_state.data)
                
                st.success(f"✅ Đã thêm yêu cầu cứu hộ mới thành công!")
                st.balloons()

with tab3:
    st.header("Phân tích địa chỉ với Gemini AI")
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ API key không hợp lệ. Vui lòng kiểm tra lại.")
    else:
        st.info("Nhập địa chỉ cần phân tích và cải thiện. Gemini AI sẽ giúp chuẩn hóa và làm rõ địa chỉ.")
        
        address_input = st.text_area(
            "Nhập địa chỉ cần phân tích",
            height=150,
            placeholder="VD: từ nhà thờ Hà Dừa đi hướng lên Diên Bình) thôn Trường Thạnh, xã Diên Thạnh"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_btn = st.button("🔍 Phân tích", type="primary")
        
        if analyze_btn and address_input:
            with st.spinner("Đang phân tích địa chỉ..."):
                improved_address, status = analyze_address_with_gemini(address_input, st.session_state.gemini_api_key)
                
                if "Quota" in status or "quota" in status.lower():
                    st.error("❌ Quota API đã hết!")
                    st.warning("⚠️ Vui lòng thử lại sau 24 giờ hoặc kiểm tra billing tại: https://ai.dev/usage?tab=rate-limit")
                    st.info("💡 Bạn vẫn có thể sử dụng địa chỉ gốc để thêm yêu cầu.")
                elif "Lỗi" in status or "Vui lòng" in status or "không hợp lệ" in status.lower():
                    st.error(f"❌ {status}")
                elif status == "Thành công" and improved_address:
                    st.success("✅ Phân tích thành công!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 Địa chỉ gốc")
                        st.text_area("", address_input, height=100, disabled=True, key="original")
                    
                    with col2:
                        st.subheader("✨ Địa chỉ đã cải thiện")
                        improved_display = st.text_area("", improved_address, height=100, key="improved")
                    
                    # Option to add to data
                    if st.button("➕ Thêm địa chỉ đã cải thiện vào dữ liệu"):
                        st.info("Vui lòng sử dụng tab 'Thêm yêu cầu mới' để thêm địa chỉ này vào hệ thống.")
                else:
                    st.warning("⚠️ Không thể cải thiện địa chỉ. Sử dụng địa chỉ gốc.")
        elif analyze_btn:
            st.warning("Vui lòng nhập địa chỉ cần phân tích.")


# Footer
st.markdown("---")
st.caption("Hệ thống Quản lý Yêu cầu Cứu hộ SOS | Powered by Streamlit & Gemini AI")

