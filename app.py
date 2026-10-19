import streamlit as st
import pandas as pd
import io
from datetime import date

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="안전보건관리 통합 시스템 - 작업계획서 제출",
    page_icon="🦺",
    layout="wide"
)

st.title("🦺 안전보건관리 시스템 (EHS Portal)")
st.caption("외부 협력업체 공사작업허가서 신청, 위험성평가 및 법정 작업계획서 통합 작성 페이지")
st.info(
    "💡 **작성 방법:** 아래 **1번 기본정보를 한 번만 입력**하시고 금번 공사에 해당하는 **위험작업을 체크**하여 작성해 주십시오. "
    "맨 아래 **[작성 완료 및 제출용 엑셀 생성]** 버튼을 누르면 모든 시트에 기본정보가 자동 입력된 엑셀 파일이 만들어집니다."
)

# ---------------------------------------------------------
# STEP 1. 공사 기본정보 입력 (1회 입력 -> 모든 시트 자동 반영)
# ---------------------------------------------------------
st.header("1. 공사 기본정보 및 작업지휘자 지정 (공통)")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        site_name = st.selectbox("사업장 구분 *", ["강동사업장", "홍천사업장", "구미사업장", "기타"])
        project_name = st.text_input("공사명 *", placeholder="예: 3층 배관 이설 및 천장 보수공사")
        work_location = st.text_input("구체적 작업장소 *", placeholder="예: 본관 3층 A구역")
    with col2:
        dept_name = st.text_input("발주 담당부서 *", placeholder="예: 시설관리파트")
        manager_name = st.text_input("발주 담당자 성명 *", placeholder="예: 홍길동")
        work_dates = st.date_input("공사 기간 *", value=(date.today(), date.today()))
    with col3:
        company_name = st.text_input("공사업체명(협력사) *", placeholder="예: (주)안전이앤씨")
        leader_name = st.text_input("현장소장 / 작업지휘자 성명 *", placeholder="법 제39조 작업지휘자 지정")
        leader_phone = st.text_input("작업지휘자 비상연락처 *", placeholder="예: 010-1234-5678")
        worker_count = st.number_input("총 투입 작업인원(명) *", min_value=1, value=2)

# ---------------------------------------------------------
# STEP 2. 위험작업 분류 선택 (체크한 항목만 하단에 열림)
# ---------------------------------------------------------
st.header("2. 위험작업 분류 선택 (해당 작업 모두 체크)")
st.caption("※ 체크하신 위험작업에 대해서만 하단에 법정 작업계획서(안전보건규칙 제38조 등) 입력창이 활성화됩니다.")

RISK_TYPES = [
    "화기/절단작업 (용접, 그라인더, 고속절단기 등)",
    "고소작업 (고소작업대, 이동식비계, 사다리 2m 이상 등)",
    "중량물 취급 작업 (화물차 상하차, 설비 반입·이설)",
    "중장비 작업 (지게차, 크레인, 굴착기 등 건설기계)",
    "전기작업 (50V / 250VA 초과 활선·정전 작업)",
    "밀폐공간 작업 (정화조, 집수조, 물탱크, 피트 내부 등)",
    "구축물·건축물 해체 / 지반 굴착작업 (2m 이상)"
]

selected_risks = st.multiselect(
    "금번 공사에 포함되는 위험작업을 모두 선택해 주세요 *",
    options=RISK_TYPES,
    default=["화기/절단작업 (용접, 그라인더, 고속절단기 등)"]
)

# ---------------------------------------------------------
# STEP 3. 안전작업절차서 (위험성평가) 및 TBM 입력
# ---------------------------------------------------------
st.header("3. 안전작업절차서(위험성평가) 및 작업 전 TBM")
st.caption("※ 아래 표의 셀을 더블클릭하여 수정하거나, 맨 아래 빈 행을 클릭해 작업 단계를 추가할 수 있습니다.")

default_jsa = pd.DataFrame([
    {"순번": 1, "작업단계": "사전준비 및 자재반입", "작업내용": "공도구 점검 및 자재 이동", "예상 위험요소": "중량물 운반 중 발 찍힘 및 넘어짐", "위험도(상/중/하)": "중", "안전대책(제거/대체/통제)": "2인 1조 운반, 안전화 착용, 이동통로 장애물 제거"},
    {"순번": 2, "작업단계": "본 작업 수행", "작업내용": "주요 설비 보수 및 설치 작업", "예상 위험요소": "작업 중 추락 또는 협착 위험", "위험도(상/중/하)": "상", "안전대책(제거/대체/통제)": "작업구획 라바콘 통제, 안전대 고리 체결 철저"},
    {"순번": 3, "작업단계": "작업 종료 및 정리정돈", "작업내용": "폐기물 반출 및 현장 정리", "예상 위험요소": "잔여 불씨 화재 및 폐기물 걸려 넘어짐", "위험도(상/중/하)": "중", "안전대책(제거/대체/통제)": "종료 후 30분 잔불 감시, 주변 정리정돈 실시"}
])

edited_jsa = st.data_editor(default_jsa, num_rows="dynamic", use_container_width=True)

# ---------------------------------------------------------
# STEP 4. 선택한 위험작업별 법정 작업계획서 & 사전조사 입력
# ---------------------------------------------------------
st.header("4. 위험작업별 법정 사전조사 및 작업계획서 작성")

plan_data = {}

if not selected_risks:
    st.warning("상단 2번 항목에서 해당되는 위험작업을 선택하거나, 일반 작업인 경우 바로 하단 엑셀 생성 버튼을 눌러주십시오.")

# 4-1. 화기/절단작업
if "화기/절단작업 (용접, 그라인더, 고속절단기 등)" in selected_risks:
    with st.expander("🔥 [필수작성] 화기/절단 작업계획 및 화재감시자 지정", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            fire_watcher = st.text_input("화재감시자 지정 성명 (법 제241조의2) *", placeholder="작업자 외 전담 감시자 성명")
            fire_equip = st.multiselect("사용 화기장비", ["전기용접기", "산소/아세틸렌", "그라인더/고속절단기", "토치/기타"], default=["그라인더/고속절단기"])
        with c2:
            fire_check1 = st.checkbox("반경 10m 이내 가연물 이격 및 불티비산방지포(방화포) 설치 완료", value=True)
            fire_check2 = st.checkbox("소화기 3개 이상 비치 및 전기용접기 자동전격방지기 부착 확인", value=True)
            fire_check3 = st.checkbox("작업 종료 후 최소 30분 이상 잔불 감시 이행 서약", value=True)
        plan_data["화기작업계획서"] = {
            "화재감시자 성명": fire_watcher,
            "사용 화기장비": ", ".join(fire_equip),
            "가연물이격 및 불티비산방지포 설치": "적합(예)" if fire_check1 else "미흡(아니오)",
            "소화기 비치 및 자동전격방지기 확인": "적합(예)" if fire_check2 else "미흡(아니오)",
            "작업 후 30분 잔불 감시 서약": "서약함" if fire_check3 else "미서약"
        }

# 4-2. 고소작업
if "고소작업 (고소작업대, 이동식비계, 사다리 2m 이상 등)" in selected_risks:
    with st.expander("🪜 [필수작성] 고소작업(고소작업대/비계/사다리) 사전조사 및 계획서", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            high_equip = st.selectbox("사용 고소장비 종류", ["시저형 고소작업대(렌탈)", "차량탑재형 고소작업대(스카이)", "이동식 비계(BT아시바)", "안전작업발판 사다리(말비계)", "A형 사다리(협소공간 예외허가)"])
            high_height = st.number_input("최대 작업 높이 (m)", min_value=1.0, value=3.5, step=0.5)
            floor_status = st.selectbox("[사전조사] 작업장소 바닥/지반 상태", ["콘크리트 평지(양호)", "아스팔트 평지(양호)", "이중바닥재(Access Floor - 보강필수)", "경사지/요철부(아웃트리거/고임목 필수)"])
        with c2:
            high_check1 = st.checkbox("작업자 안전모 및 안전대(안전고리 체결) 착용 완료", value=True)
            high_check2 = st.checkbox("아웃트리거 최대 확장 / 바퀴 구름방지(고임목) 조치 완료", value=True)
            high_check3 = st.checkbox("과상승방지장치·비상하강장치 작동 확인 및 하부 통제선(라바콘) 설치", value=True)
        plan_data["고소작업계획서"] = {
            "사용 고소장비 종류": high_equip,
            "최대 작업 높이(m)": f"{high_height} m",
            "[사전조사] 바닥 및 지반상태": floor_status,
            "안전모 및 안전대 고리 체결": "적합" if high_check1 else "미흡",
            "아웃트리거/고임목 전도방지 조치": "적합" if high_check2 else "미흡",
            "과상승방지장치 및 하부 통제구역 설정": "적합" if high_check3 else "미흡"
        }

# 4-3. 중량물 취급 작업
if "중량물 취급 작업 (화물차 상하차, 설비 반입·이설)" in selected_risks:
    with st.expander("📦 [필수작성] 중량물 취급 작업계획서 (법 제38조 제1항 제11호)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            heavy_item = st.text_input("취급 중량물 품명 및 규격(가로×세로×높이)", placeholder="예: 공조기 모터 (120cm × 80cm × 100cm)")
            heavy_weight = st.number_input("최대 중량 (kg)", min_value=10, value=250, step=10)
            heavy_tool = st.multiselect("사용 운반기구", ["핸드팔레트(자키)", "전동대차/일반대차", "체인블록/윈치", "지게차/크레인 연계", "인력운반(2인1조)"], default=["핸드팔레트(자키)"])
        with c2:
            heavy_route = st.text_input("[사전조사] 운반 경로 바닥 단차·장애물 조사 결과", value="운반경로 내 단차 없음 및 통로 폭 확보 완료")
            heavy_check1 = st.checkbox("추락·낙하·전도·협착·붕괴 5대 위험 예방대책 수립 (로프 결속, 고임목 등)", value=True)
        plan_data["중량물취급계획서"] = {
            "중량물 품명 및 규격": heavy_item,
            "최대 중량(kg)": f"{heavy_weight} kg",
            "사용 운반기구": ", ".join(heavy_tool),
            "[사전조사] 운반경로 바닥 및 장애물 상태": heavy_route,
            "추락·낙하·전도·협착·붕괴 예방조치": "수립 완료" if heavy_check1 else "미수립"
        }

# 4-4. 중장비 작업 (지게차/크레인/건설기계)
if "중장비 작업 (지게차, 크레인, 굴착기 등 건설기계)" in selected_risks:
    with st.expander("🚜 [필수작성] 중장비(지게차·크레인·건설기계) 작업계획서 (법 제38조)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            equip_type = st.selectbox("투입 장비 종류", ["지게차", "이동식 크레인(카고/하이드로)", "굴착기(백호)", "로더/롤러/기타 건설기계"])
            equip_spec = st.text_input("장비 모델명 / 규격(톤수) / 등록번호", placeholder="예: 두산 3톤 지게차 / 경기00가0000")
            driver_info = st.text_input("운전원 성명 및 면허/자격 번호", placeholder="예: 김운전 (건설기계조종사면허 확인필)")
            signal_man = st.text_input("전담 유도자(신호수) 성명 *", placeholder="예: 이신호")
        with c2:
            ground_survey = st.text_input("[사전조사] 지형·지반 침하 우려 및 상부 전선/매설물 유무", value="견고한 콘크리트 지반, 회전반경 내 가공전선 및 장애물 없음")
            equip_check1 = st.checkbox("장비 보험가입증명서, 검사유효기간, 운전원 면허증 사전 확인 완료", value=True)
            equip_check2 = st.checkbox("후방카메라, 후진경보기, 과부하방지장치(크레인), 퀵커플러 안전핀(굴착기) 점검 양호", value=True)
        plan_data["중장비작업계획서"] = {
            "투입 장비 종류": equip_type,
            "장비 규격 및 등록번호": equip_spec,
            "운전원 및 자격": driver_info,
            "유도자(신호수) 성명": signal_man,
            "[사전조사] 지형·지반 및 장애물 조사결과": ground_survey,
            "보험·검사·면허 서류 확인": "확인 완료" if equip_check1 else "미확인",
            "법정 안전장치(후방경보·과부하방지 등) 점검": "양호" if equip_check2 else "불량"
        }

# 4-5. 전기작업
if "전기작업 (50V / 250VA 초과 활선·정전 작업)" in selected_risks:
    with st.expander("⚡ [필수작성] 전기작업계획서 (법 제38조 제1항 제5호)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            elec_voltage = st.text_input("취급 전압 및 작업 대상 설비", placeholder="예: AC 380V 분전반 차단기 교체")
            elec_method = st.radio("작업 방식", ["정전 작업 (전원 차단 후 작업 원칙)", "활선 근접 작업 (방호구 및 절연보호구 필수)"])
        with c2:
            elec_loto = st.checkbox("[필수] 전원 차단 후 잠금장치(LOTO) 체결 및 통전금지 표지판 부착", value=True)
            elec_test = st.checkbox("[필수] 잔류전하 방전 조치 및 검전기로 무전압 상태 확인", value=True)
            elec_ppe = st.checkbox("절연장갑, 절연화, 절연안전모(ABE종) 착용 완료", value=True)
        plan_data["전기작업계획서"] = {
            "취급 전압 및 대상 설비": elec_voltage,
            "작업 방식": elec_method,
            "전원차단 및 LOTO(잠금/표지) 실시": "완료" if elec_loto else "미실시",
            "잔류전하 방전 및 검전기 확인": "완료" if elec_test else "미실시",
            "절연용 보호구 착용 여부": "착용 완료" if elec_ppe else "미착용"
        }

# 4-6. 밀폐공간 작업
if "밀폐공간 작업 (정화조, 집수조, 물탱크, 피트 내부 등)" in selected_risks:
    with st.expander("😷 [필수작성] 밀폐공간 보건작업 프로그램 및 산소·유해가스 측정 계획 (법 제619조)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            confined_place = st.text_input("밀폐공간 구체적 명칭", placeholder="예: 지하 2층 집수정 내부")
            confined_watcher = st.text_input("외부 상주 감시인 성명 (규칙 제623조) *", placeholder="예: 박감시 (무전기 교신)")
            gas_result = st.text_input("[작업 전 측정] 산소(18~23.5%), CO(<30ppm), H2S(<10ppm) 측정치", placeholder="예: O2 20.9%, CO 0ppm, H2S 0ppm (적합)")
        with c2:
            conf_check1 = st.checkbox("작업 전·중 강제 급배기 환기팬 상시 가동 완료", value=True)
            conf_check2 = st.checkbox("비상 구출용 송기마스크(또는 공기호흡기) 및 삼각대/구명줄 비치 완료", value=True)
            conf_check3 = st.checkbox("출입 전·후 작업자 인원 계수 및 호흡보호구 미착용 구조 진입 절대 금지 교육 완료", value=True)
        plan_data["밀폐공간작업계획서"] = {
            "밀폐공간 명칭": confined_place,
            "외부 전담 감시인": confined_watcher,
            "산소 및 유해가스 측정 결과": gas_result,
            "강제 환기설비 상시 가동": "완료" if conf_check1 else "미흡",
            "송기마스크/공기호흡기 및 구출삼각대 비치": "완료" if conf_check2 else "미흡",
            "출입인원 점검 및 비상구조 교육": "완료" if conf_check3 else "미흡"
        }

# 4-7. 해체 / 굴착작업
if "구축물·건축물 해체 / 지반 굴착작업 (2m 이상)" in selected_risks:
    with st.expander("🏗️ [필수작성] 구축물 해체 / 지반 굴착(2m 이상) 작업계획서 (법 제38조)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            demo_target = st.text_input("해체 구조물 또는 굴착 규모(깊이 m)", placeholder="예: 2층 가벽 철거 (높이 3m) / 배관 매설 굴착 (깊이 2.2m)")
            demo_survey = st.text_input("[사전조사] 내부 매설물(전선/가스/수도관), 석면 유무, 지층 상태 조사 결과", value="도면 확인 결과 매설선 차단 완료, 무석면 확인 완료")
        with c2:
            demo_method = st.text_input("해체 순서(상부→하부) 또는 굴착면 기울기/흙막이 설치 계획", value="상부 천장재 선 철거 후 벽체 해체 / 하부 통행금지 구획")
            demo_check = st.checkbox("붕괴 방지 지지대(또는 흙막이) 설치 및 단부 중량물 적재 금지 조치 완료", value=True)
        plan_data["해체및굴착작업계획서"] = {
            "해체 구조물 / 굴착 규모": demo_target,
            "[사전조사] 매설물·석면·지반 상태": demo_survey,
            "해체 순서 및 굴착 붕괴방지 방법": demo_method,
            "지지대/흙막이 및 단부 안전조치": "완료" if demo_check else "미흡"
        }

# ---------------------------------------------------------
# STEP 5. 엑셀 파일(.xlsx) 자동 생성 및 다운로드
# ---------------------------------------------------------
st.divider()
st.subheader("5. 통합 작업계획서 엑셀 파일(.xlsx) 생성 및 제출")

def generate_excel():
    output = io.BytesIO()
    date_str = f"{work_dates[0]} ~ {work_dates[1]}" if len(work_dates) == 2 else str(work_dates[0])

    # 모든 시트 상단에 자동으로 들어갈 공통 기본정보 표
    common_header = pd.DataFrame([
        ["사업장", site_name, "발주부서 / 담당자", f"{dept_name} / {manager_name}"],
        ["공사명", project_name, "공사업체명", company_name],
        ["공사기간", date_str, "작업장소 / 인원", f"{work_location} / {worker_count}명"],
        ["작업지휘자(법 제39조 지정)", f"{leader_name} ({leader_phone})", "적용 위험작업", ", ".join(selected_risks)]
    ], columns=["구분1", "내용1", "구분2", "내용2"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 시트 1: 공사작업허가서 (표지)
        common_header.to_excel(writer, sheet_name="1_공사작업허가서", index=False, startrow=1)

        # 시트 2: 안전작업절차서(위험성평가) 및 TBM
        common_header.to_excel(writer, sheet_name="2_안전작업절차서_TBM", index=False, startrow=1)
        edited_jsa.to_excel(writer, sheet_name="2_안전작업절차서_TBM", index=False, startrow=8)

        # 시트 3~: 선택된 위험작업별 작업계획서 시트 자동 생성
        sheet_idx = 3
        for sheet_title, details in plan_data.items():
            s_name = f"{sheet_idx}_{sheet_title}"[:31]
            common_header.to_excel(writer, sheet_name=s_name, index=False, startrow=1)

            detail_df = pd.DataFrame(list(details.items()), columns=["법정 필수 점검·계획 항목", "작성 및 사전조사 내용"])
            detail_df.to_excel(writer, sheet_name=s_name, index=False, startrow=8)

            # 근로자 주지 확인 서명란 (법 제38조 제2항)
            sign_df = pd.DataFrame([
                ["[법 제38조 제2항 확인]", "본 작업계획서의 사전조사 결과, 작업순서 및 안전대책을 전 작업자에게 교육·주지시켰음을 확인합니다."],
                ["교육일시 / 작업지휘자 서명", f"{date.today()} / 작업지휘자: {leader_name} (인)"],
                ["참석 근로자 서명", "① (인)   ② (인)   ③ (인)   ④ (인)   ⑤ (인)"]
            ], columns=["구분", "확인 내용"])
            sign_df.to_excel(writer, sheet_name=s_name, index=False, startrow=10 + len(detail_df))
            sheet_idx += 1

    output.seek(0)
    return output

if st.button("✅ 작성 완료 및 제출용 엑셀 생성", type="primary", use_container_width=True):
    if not project_name or not company_name or not leader_name:
        st.error("🚨 '1. 공사 기본정보'의 필수 항목(공사명, 공사업체명, 작업지휘자 성명)을 모두 입력해 주세요.")
    else:
        excel_file = generate_excel()
        file_name = f"[작업계획서통합본]_{company_name}_{project_name}_{date.today()}.xlsx"
        st.success("🎉 모든 시트에 기본정보와 법정 사전조사 내용이 반영된 엑셀 파일이 생성되었습니다! 아래 버튼을 눌러 다운로드 후 담당자에게 제출하세요.")
        st.download_button(
            label="📥 완성된 작업계획서 엑셀 파일(.xlsx) 다운로드",
            data=excel_file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
