# py-sodas-sdk

SODAS 프레임워크를 위한 공식 Python SDK입니다. 
이 SDK를 통해 데이터셋의 메타데이터를 효율적으로 관리하고 표준화된 방식으로 처리할 수 있습니다. 
DCAT(Data Catalog Vocabulary) 표준을 기반으로 하여 데이터셋의 메타데이터를 체계적으로 관리할 수 있습니다.

## 설치 방법

```bash
pip install py-sodas-sdk
```

## 주요 기능

- 데이터셋 메타데이터 생성 및 관리 (DCAT 기반)
- 다국어 메타데이터 지원 (제목, 설명, 키워드 등)
- 프로파일 기반의 메타데이터 스키마 관리
- 리소스 설명자를 통한 데이터 리소스 관리
- 버전 관리 및 이력 추적

## 핵심 컴포넌트

### DatasetDTO

데이터셋의 메타데이터를 관리하는 핵심 클래스입니다.

```python
from sodas_sdk import DatasetDTO

dataset = DatasetDTO()

# 기본 메타데이터 설정
dataset.set_title("데이터셋 제목")
dataset.set_description("데이터셋 설명")
dataset.set_type("http://purl.org/dc/dcmitype/Dataset")

# 다국어 지원
dataset.set_title_ml({
    "ko": "한글 제목",
    "en": "English Title"
})

# 접근 권한 및 라이선스
dataset.set_access_rights("http://purl.org/eprint/accessRights/OpenAccess")
dataset.set_license("http://creativecommons.org/licenses/by/4.0/")
```

### Profile

메타데이터 프로파일을 정의하고 관리하는 클래스입니다.


### ResourceDescriptor

데이터 리소스의 구조와 특성을 기술하는 클래스입니다.


## API 초기화

SDK를 사용하기 전에 반드시 API URL을 초기화해야 합니다:

```python
from sodas_sdk import initialize_api_urls

DATAHUB_API_URL = "http://sodas-profile.example.com"
GOVERNANCE_API_URL = "http://api.example.com"

initialize_api_urls(DATAHUB_API_URL, GOVERNANCE_API_URL)
