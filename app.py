import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import google.generativeai as genai

# Page config
st.set_page_config(
    page_title="Hệ thống Cứu hộ SOS",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default Gemini API Key
DEFAULT_GEMINI_API_KEY = "AIzaSyDjKUsmoQ_uaCImS1O--vUM0jUzo_bOo7I"

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
        # Sử dụng gemini-1.5-flash vì có trong free tier và ổn định hơn
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
    
    with st.form("add_rescue_request", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox(
                "Mức độ ưu tiên *",
                ["Khẩn cấp", "Cao", "Trung bình", "Thấp"],
                index=0
            )
            
            area = st.text_input("Chi tiết khu vực *")
            
            num_people = st.text_input("Số người", placeholder="VD: 5, Nhiều, 10-15")
        
        with col2:
            address = st.text_area("Địa chỉ *", height=100, placeholder="Nhập địa chỉ chi tiết...")
            
            phone = st.text_input("Số điện thoại", placeholder="VD: 0912345678, 0901234567")
        
        st.info("ℹ️ Địa chỉ sẽ tự động được cải thiện bằng Gemini AI khi thêm yêu cầu.")
        
        submitted = st.form_submit_button("➕ Thêm yêu cầu", type="primary")
        
        if submitted:
            # Validation
            if not area or not address:
                st.error("Vui lòng điền đầy đủ các trường bắt buộc (*)")
            else:
                # Automatically improve address with Gemini
                final_address = address
                if st.session_state.gemini_api_key:
                    with st.spinner("🔄 Đang tự động phân tích và cải thiện địa chỉ với Gemini AI..."):
                        final_address, status = analyze_address_with_gemini(address, st.session_state.gemini_api_key)
                        if "Quota" in status or "quota" in status.lower():
                            st.warning("⚠️ Quota API đã hết. Sử dụng địa chỉ gốc. Vui lòng thử lại sau hoặc kiểm tra billing.")
                            final_address = address
                        elif "Lỗi" in status or "Vui lòng" in status or "không hợp lệ" in status.lower():
                            st.warning(f"⚠️ {status}. Sử dụng địa chỉ gốc.")
                            final_address = address
                        elif status == "Thành công" and final_address != address:
                            st.success("✅ Đã tự động cải thiện địa chỉ!")
                            st.info(f"**Địa chỉ gốc:** {address}\n\n**Địa chỉ đã cải thiện:** {final_address}")
                        else:
                            # Địa chỉ không thay đổi hoặc không cần cải thiện
                            final_address = address
                
                # Create new row
                new_row = pd.DataFrame({
                    'Mức độ ưu tiên': [priority],
                    'Chi tiết khu vực': [area],
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

