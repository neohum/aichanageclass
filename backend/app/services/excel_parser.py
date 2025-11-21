"""
Excel 파일 파싱 서비스
"""
import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ExcelParser:
    """Excel 파일 파싱 및 검증"""
    
    # 필수 컬럼 (한글)
    REQUIRED_COLUMNS = ['학년', '이름', '성별']
    
    # 선택 컬럼 (있으면 좋은 것들)
    OPTIONAL_COLUMNS = ['반', '번호']
    
    # 성별 매핑
    GENDER_MAPPING = {
        '남': '남',
        '여': '여',
        'M': '남',
        'F': '여',
        'male': '남',
        'female': '여',
        '남자': '남',
        '여자': '여'
    }
    
    @staticmethod
    def parse_excel(file_path: str) -> Tuple[List[Dict], List[str], List[Dict]]:
        """
        Excel 파일 파싱
        
        Args:
            file_path: Excel 파일 경로
            
        Returns:
            (학생 데이터 리스트, 커스텀 컬럼 리스트, 필드 정의 리스트)
        """
        try:
            # Excel 파일 읽기
            df = pd.read_excel(file_path)
            logger.info(f"Excel 파일 로드 완료: {len(df)}행, {len(df.columns)}열")
            
            # 컬럼명 정리 (공백 제거)
            df.columns = df.columns.str.strip()
            
            # 필수 컬럼 확인
            missing_cols = [col for col in ExcelParser.REQUIRED_COLUMNS 
                           if col not in df.columns]
            if missing_cols:
                raise ValueError(f"필수 컬럼이 없습니다: {', '.join(missing_cols)}")
            
            # 커스텀 컬럼 추출
            all_standard_cols = ExcelParser.REQUIRED_COLUMNS + ExcelParser.OPTIONAL_COLUMNS
            custom_columns = [col for col in df.columns if col not in all_standard_cols]
            logger.info(f"커스텀 컬럼: {custom_columns}")
            
            # 필드 정의 자동 생성
            field_definitions = ExcelParser._generate_field_definitions(df, custom_columns)
            
            # 데이터 변환
            students = []
            for idx, row in df.iterrows():
                try:
                    student_data = ExcelParser._parse_student_row(row, custom_columns)
                    students.append(student_data)
                except Exception as e:
                    logger.warning(f"행 {idx + 2} 파싱 오류: {e}")
                    continue
            
            logger.info(f"총 {len(students)}명의 학생 데이터 파싱 완료")
            return students, custom_columns, field_definitions
            
        except Exception as e:
            logger.error(f"Excel 파싱 오류: {e}")
            raise
    
    @staticmethod
    def _parse_student_row(row: pd.Series, custom_columns: List[str]) -> Dict:
        """개별 학생 행 파싱"""
        # 성별 정규화
        gender_raw = str(row['성별']).strip()
        gender = ExcelParser.GENDER_MAPPING.get(gender_raw, gender_raw)
        
        student_data = {
            'grade': int(row['학년']),
            'name': str(row['이름']).strip(),
            'gender': gender,
            'custom_fields': {}
        }
        
        # 선택 필드
        if '반' in row.index and pd.notna(row['반']):
            student_data['original_class'] = int(row['반'])
        
        if '번호' in row.index and pd.notna(row['번호']):
            student_data['number'] = int(row['번호'])
        
        # 커스텀 필드 추가
        for col in custom_columns:
            value = row[col]
            if pd.notna(value):
                # 타입 변환
                if isinstance(value, (int, float)):
                    student_data['custom_fields'][col] = float(value) if '.' in str(value) else int(value)
                elif isinstance(value, bool):
                    student_data['custom_fields'][col] = value
                else:
                    student_data['custom_fields'][col] = str(value).strip()
        
        return student_data
    
    @staticmethod
    def _generate_field_definitions(df: pd.DataFrame, custom_columns: List[str]) -> List[Dict]:
        """커스텀 필드 정의 자동 생성"""
        field_definitions = []
        
        for col in custom_columns:
            # 샘플 데이터로 타입 추론
            sample_values = df[col].dropna().head(10)
            
            if len(sample_values) == 0:
                continue
            
            field_def = {
                "name": col,
                "required": False
            }
            
            # 타입 추론
            first_value = sample_values.iloc[0]
            
            if isinstance(first_value, bool):
                field_def["type"] = "boolean"
            elif isinstance(first_value, (int, float)):
                field_def["type"] = "number"
                # 범위 추정
                field_def["min"] = float(sample_values.min())
                field_def["max"] = float(sample_values.max())
            else:
                # 문자열 - 선택지가 적으면 select, 많으면 text
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 10:
                    field_def["type"] = "select"
                    field_def["options"] = [str(v) for v in unique_values]
                else:
                    field_def["type"] = "text"
            
            field_definitions.append(field_def)
        
        return field_definitions
    
    @staticmethod
    def validate_data(students: List[Dict]) -> List[str]:
        """데이터 검증"""
        errors = []
        
        for idx, student in enumerate(students, 1):
            # 이름 확인
            if not student.get('name') or student['name'].strip() == '':
                errors.append(f"행 {idx}: 이름이 비어있습니다")
            
            # 성별 확인
            if student.get('gender') not in ['남', '여']:
                errors.append(f"행 {idx}: 성별이 올바르지 않습니다 ({student.get('gender')})")
            
            # 학년 확인
            grade = student.get('grade')
            if not grade or grade < 1 or grade > 6:
                errors.append(f"행 {idx}: 학년이 올바르지 않습니다 ({grade})")
        
        return errors
    
    @staticmethod
    def export_to_excel(students: List[Dict], output_path: str, custom_columns: List[str]):
        """학생 데이터를 Excel로 내보내기"""
        # 데이터 변환
        rows = []
        for student in students:
            row = {
                '학년': student['grade'],
                '반': student.get('assigned_class', student.get('original_class', '')),
                '번호': student.get('number', ''),
                '이름': student['name'],
                '성별': student['gender']
            }
            
            # 커스텀 필드 추가
            for col in custom_columns:
                row[col] = student.get('custom_fields', {}).get(col, '')
            
            rows.append(row)
        
        # DataFrame 생성 및 저장
        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)
        logger.info(f"Excel 파일 저장 완료: {output_path}")

