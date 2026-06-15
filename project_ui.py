import streamlit as st
import base64
import json
import os
from datetime import datetime

def show_project_hub():
    st.header("📁 ระบบจัดการโปรเจกต์รวม (Project Hub)")  # 👈 เพิ่มไว้บนสุดของไฟล์ หรือในฟังก์ชันก็ได้ครับ
    

    # กำหนดชื่อไฟล์เซฟด่วนที่จะเก็บไว้ในเครื่องคอมพิวเตอร์ของเรา
    LOCAL_SAVE_FILE = "local_quick_save.json"

    st.markdown("---")
    st.subheader("💾 ระบบบันทึกด่วนลงคอมพิวเตอร์ (Quick Local Save & Load)")
    st.write("บันทึกข้อมูลคาน พื้น และตะกร้า PDF ลงในฮาร์ดดิสก์ของคุณทันที โดยไม่ต้องดาวน์โหลดผ่านเบราว์เซอร์")

    save_col1, save_col2 = st.columns(2)

    # ==========================================
    # 📌 ฝั่งปุ่มกด SAVE (เซฟงานลงคอมทันที)
    # ==========================================
    with save_col1:
        if st.button("💾 เซฟงานปัจจุบันลงคอมพิวเตอร์ทันที", type="primary", use_container_width=True):
            try:
                # 1. จัดการแปลงไฟล์ PDF ในตะกร้าให้กลายเป็นข้อความ Base64 เพื่อให้เซฟลง JSON ได้
                serializable_pdf_queue = []
                for item in st.session_state.get("pdf_queue", []):
                    serializable_pdf_queue.append({
                        "id": item["id"],
                        "name": item["name"],
                        "bytes_b64": base64.b64encode(item["bytes"]).decode("utf-8") # แปลงร่างเป็น Text
                    })

                # 2. มัดรวมข้อมูลทุกอย่างเข้าด้วยกัน
                save_bundle = {
                    "project_name": st.session_state.get("project_name", "My Project"),
                    "beam_library": st.session_state.get("beam_library", {}),
                    "slab_library": st.session_state.get("slab_library", {}),
                    "pdf_queue": serializable_pdf_queue # มัดตะกร้า PDF ไปด้วย
                }

                # 3. เขียนไฟล์ลง Harddisk ตรงๆ ซื่อๆ เลย
                with open(LOCAL_SAVE_FILE, "w", encoding="utf-8") as f:
                    json.dump(save_bundle, f, indent=4, ensure_ascii=False)

                st.success(f"✅ บันทึกงานสำเร็จลงไฟล์ '{LOCAL_SAVE_FILE}' เรียบร้อยแล้ว! (เวลา {datetime.now().strftime('%H:%M:%S')})")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการบันทึก: {e}")

    # ==========================================
    # 📌 ฝั่งปุ่มกด LOAD (ดึงงานล่าสุดกลับมาทำต่อ)
    # ==========================================
    with save_col2:
        # เช็คก่อนว่ามีไฟล์เซฟเก่าอยู่ในเครื่องไหม ถ้าไม่มีให้ปิดปุ่มไว้กันแอปพัง
        file_exists = os.path.exists(LOCAL_SAVE_FILE)
        
        if st.button("🔄 โหลดงานล่าสุดจากคอมพิวเตอร์", use_container_width=True, disabled=not file_exists):
            try:
                # 1. เปิดอ่านไฟล์จากฮาร์ดดิสก์
                with open(LOCAL_SAVE_FILE, "r", encoding="utf-8") as f:
                    loaded_bundle = json.load(f)

                # 2. คืนค่าให้กับสมองส่วนกลางของแอป
                st.session_state.project_name = loaded_bundle.get("project_name", "Project Loaded")
                st.session_state.beam_library = loaded_bundle.get("beam_library", {})
                st.session_state.slab_library = loaded_bundle.get("slab_library", {})

                # 3. แปลงค่าข้อความ Base64 กลับมาเป็นไฟล์ PDF ข้อมูลดิบเหมือนเดิม
                restored_pdf_queue = []
                for item in loaded_bundle.get("pdf_queue", []):
                    restored_pdf_queue.append({
                        "id": item["id"],
                        "name": item["name"],
                        "bytes": base64.b64decode(item["bytes_b64"].encode("utf-8")) # แปลงกลับเป็นไฟล์จริง
                    })
                st.session_state.pdf_queue = restored_pdf_queue

                st.success("🎉 โหลดข้อมูลคาน พื้น และรายการ PDF ทั้งหมดกลับมาเรียบร้อยแล้ว!")
                st.rerun() # รีเฟรชหน้าจอโชว์ความสำเร็จทันที
                
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการโหลดไฟล์เซฟ: {e}")
    st.write("หน้านี้คือศูนย์กลางควบคุมข้อมูลโครงสร้างทั้งอาคาร คุณสามารถตั้งชื่อโปรเจกต์ สรุปรายการวัสดุ และบันทึก/โหลดไฟล์โครงสร้างทั้งหมดได้ในไฟล์เดียว")
    st.markdown("---")
    
    c1, c2 = st.columns(2, gap="large")
    
    # ------------------------------------------
    # 📤 บันทึกโปรเจกต์ (ส่งออกไฟล์ครอบจักรวาล)
    # ------------------------------------------
    with c1:
        st.subheader("📤 บันทึกโปรเจกต์ออกเป็นไฟล์ (Export Project)")
        st.session_state.project_name = st.text_input("ระบุชื่อโปรเจกต์ / ชื่ออาคาร:", value=st.session_state.project_name)
        
        # มัดรวมข้อมูลจากคลังคานและคลังพื้นเข้าด้วยกันเป็นก้อนเดียว
        full_project_bundle = {
            "project_name": st.session_state.project_name,
            "beam_library": st.session_state.beam_library,
            "slab_library": st.session_state.slab_library
        }
        
        # แปลงข้อมูลทั้งหมดเป็นข้อความสำหรับทำไฟล์ JSON
        json_string = json.dumps(full_project_bundle, indent=4, ensure_ascii=False)
        
        st.write(f"📊 ปัจจุบันมีข้อมูลคานที่บันทึกในตึกนี้: `{len(st.session_state.beam_library)}` ประเภท")
        st.write(f"📊 ปัจจุบันมีข้อมูลพื้นที่บันทึกในตึกนี้: `{len(st.session_state.slab_library)}` ประเภท")
        
        st.download_button(
            label="💾 ดาวน์โหลดไฟล์โปรเจกต์รวม (.json)",
            data=json_string,
            file_name=f"{st.session_state.project_name}_Structure_Data.json",
            mime="application/json",
            use_container_width=True
        )
        
    # ------------------------------------------
    # 📥 โหดลไฟล์โปรเจกต์เดิมเข้ามาทำต่อ
    # ------------------------------------------
    with c2:
        st.subheader("📥 โหลดไฟล์โปรเจกต์เดิม (Import Project)")
        st.write("อัปโหลดไฟล์โปรเจกต์ .json ของคุณ ข้อมูลคานและพื้นทั้งหมดจะเด้งกลับมาทำต่อทันที")
        
        uploaded_file = st.file_uploader("เลือกไฟล์โปรเจกต์รวมที่นี่", type=["json"])
        
        if uploaded_file is not None:
            # 🛑 สร้างปุ่มดักไว้! ป้องกันเว็บแอบโหลดไฟล์ทับข้อมูลตอนเรารีเฟรชหรือกดลบ
            if st.button("📥 ยืนยันการโหลดข้อมูลจากไฟล์", type="primary", use_container_width=True):
                try:
                    loaded_bundle = json.load(uploaded_file)
                    
                    # โคลนนิ่งข้อมูลจากไฟล์ยัดกลับเข้าสมองส่วนกลางแอป
                    st.session_state.project_name = loaded_bundle.get("project_name", "Project Loaded")
                    st.session_state.beam_library = loaded_bundle.get("beam_library", {})
                    st.session_state.slab_library = loaded_bundle.get("slab_library", {})
                    
                    st.success(f"🎉 โหลดโปรเจกต์ '{st.session_state.project_name}' เรียบร้อย!")
                    st.rerun() # 👈 ใส่ st.rerun() คืนตรงนี้ได้เลยครับ เพราะมันอยู่ในปุ่มแล้ว จะไม่ลูปรัวๆ แน่นอน
                    
                except Exception as e:
                    st.error("❌ รูปแบบไฟล์ไม่ถูกต้อง หรือข้อมูลภายในไฟล์เสียหาย")
    # 📋 รายงานสรุปหน้าตาตึก
    # =========================================================================
    # 📋 รายการชิ้นส่วนโครงสร้างในระบบปัจจุบัน (Data Inventory)
    # =========================================================================
    st.markdown("---")
    st.subheader("📋 รายการชิ้นส่วนโครงสร้างในระบบปัจจุบัน (Data Inventory)")
    
    inv_c1, inv_c2 = st.columns(2)
    
    with inv_c1:
        st.markdown("**🏗️ รายชื่อคานที่เคยบันทึกไว้:**")
        if "beam_library" in st.session_state and st.session_state.beam_library:
            # 💡 ทริค: ต้องครอบด้วย list() เพื่อป้องกัน Error เวลาลบข้อมูลตอนกำลังวนลูป
            for beam_name in list(st.session_state.beam_library.keys()):
                b_col1, b_col2 = st.columns([4, 1]) # แบ่งสัดส่วน ชื่อยาว 4 ส่วน ปุ่มลบ 1 ส่วน
                with b_col1:
                    st.success(f"✅ {beam_name}")
                with b_col2:
                    if st.button("🗑️", key=f"del_beam_{beam_name}", use_container_width=True):
                        del st.session_state.beam_library[beam_name] # ลบออกจากความจำ
                        st.rerun() # รีเฟรชหน้าต่างทันที
        else:
            st.caption("ยังไม่มีข้อมูลคานถูกบันทึก")
            
    with inv_c2:
        st.markdown("**🔲 รายชื่อแผ่นพื้นที่เคยบันทึกไว้:**")
        if "slab_library" in st.session_state and st.session_state.slab_library:
            for slab_name in list(st.session_state.slab_library.keys()):
                s_col1, s_col2 = st.columns([4, 1])
                with s_col1:
                    st.success(f"✅ {slab_name}")
                with s_col2:
                    if st.button("🗑️", key=f"del_slab_{slab_name}", use_container_width=True):
                        del st.session_state.slab_library[slab_name]
                        st.rerun()
        else:
            st.caption("ยังไม่มีข้อมูลพื้นถูกบันทึก")