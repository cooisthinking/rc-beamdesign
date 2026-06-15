import streamlit as st
import io
from pypdf import PdfWriter
import fitz  # 👈 นำเข้า PyMuPDF สำหรับทำรูปพรีวิว

def show_pdf_manager():
    st.header("📑 ระบบจัดการและรวมไฟล์ PDF (PDF Manager)")
    st.write("ตรวจสอบความถูกต้อง สลับตำแหน่ง หรือลบไฟล์ที่ไม่ต้องการก่อนทำการรวมเล่ม")
    st.markdown("---")

    queue = st.session_state.pdf_queue

    if len(queue) == 0:
        st.info("📭 ตะกร้ายังว่างเปล่า! ไปที่แท็บ RC Beam หรือ RC Slab แล้วกดปุ่ม 'เก็บลงตะกร้า' เพื่อส่งไฟล์มาที่นี่")
        return

    # ========================================================
    # 🌟 1. ส่วนแสดงการ์ดพรีวิว PDF (จำลองระบบ Drag & Drop ด้วยปุ่ม)
    # ========================================================
    # สร้างกริด 3 คอลัมน์
    cols = st.columns(3) 
    
    for i, item in enumerate(queue):
        col = cols[i % 3] # วนลูปวางการ์ดในคอลัมน์ 1 -> 2 -> 3
        
        with col:
            st.markdown(f"<div style='text-align: center; background-color: var(--secondary-background-color); padding: 10px; border-radius: 10px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            
            # --- สร้างรูป Thumbnail พรีวิวจากหน้าแรกของ PDF ---
            try:
                doc = fitz.open(stream=item["bytes"], filetype="pdf")
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=100) # ความละเอียดพอดีๆ
                st.image(pix.tobytes("png"), use_container_width=True)
            except Exception:
                st.warning("⚠️ ไม่สามารถพรีวิวได้")
            
            # --- ชื่อไฟล์และปุ่มควบคุม ---
            st.caption(f"**{i+1}. {item['name']}**")
            
            # แบ่ง 3 ช่องเล็กๆ สำหรับปุ่ม [ซ้าย] [ลบ] [ขวา]
            btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 1])
            with btn_c1:
                if st.button("◀️", key=f"L_{i}", use_container_width=True, disabled=(i == 0)):
                    queue[i], queue[i-1] = queue[i-1], queue[i] # สลับที่กับตัวซ้าย
                    st.rerun()
            with btn_c2:
                if st.button("🗑️", key=f"D_{i}", use_container_width=True):
                    queue.pop(i) # ลบทิ้ง
                    st.rerun()
            with btn_c3:
                if st.button("▶️", key=f"R_{i}", use_container_width=True, disabled=(i == len(queue) - 1)):
                    queue[i], queue[i+1] = queue[i+1], queue[i] # สลับที่กับตัวขวา
                    st.rerun()
                    
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ========================================================
    # 🌟 2. ระบบรวมไฟล์ (Merge PDF)
    # ========================================================
    st.subheader("📦 รวมไฟล์ทั้งหมด (Merge Documents)")
    
    if st.button("🔄 ผสานไฟล์ PDF ทั้งหมดตอนนี้", type="primary", use_container_width=True):
        try:
            merger = PdfWriter()
            
            # นำ PDF ทุกตัวในตะกร้ามาต่อกัน
            for item in queue:
                pdf_stream = io.BytesIO(item["bytes"])
                merger.append(pdf_stream)
                
            # ส่งออกเป็นไฟล์ใหม่
            merged_pdf_stream = io.BytesIO()
            merger.write(merged_pdf_stream)
            merger.close()
            
            final_pdf_bytes = merged_pdf_stream.getvalue()
            
            st.success("🎉 รวมไฟล์สำเร็จ! กดปุ่มด้านล่างเพื่อดาวน์โหลดได้เลย")
            st.download_button(
                label="💾 ดาวน์โหลดไฟล์เอกสารรวม (Merged PDF)",
                data=final_pdf_bytes,
                file_name=f"Complete_Report_{st.session_state.project_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการรวมไฟล์: {e}")