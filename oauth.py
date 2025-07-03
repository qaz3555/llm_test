import httpx
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

KEYCLOAK_AUTH_URL = "https://your-keycloak.com/realms/your-realm/protocol/openid-connect/auth"
KEYCLOAK_TOKEN_URL = "https://your-keycloak.com/realms/your-realm/protocol/openid-connect/token"
KEYCLOAK_USERINFO_URL = "https://your-keycloak.com/realms/your-realm/protocol/openid-connect/userinfo"

DEPARTMENT_GROUP = "it-dept"  # 你們部門的名稱（需與 Keycloak 設定一致）

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=KEYCLOAK_AUTH_URL,
    tokenUrl=KEYCLOAK_TOKEN_URL
)

# 驗證 token 並檢查是否屬於指定部門
async def check_group(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(KEYCLOAK_USERINFO_URL, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        userinfo = resp.json()
        groups = userinfo.get("groups", [])

        if DEPARTMENT_GROUP not in groups:
            raise HTTPException(status_code=403, detail="You are not allowed to view this resource")

# 自定義 /docs 並加上部門群組檢查
@app.get("/docs", include_in_schema=False)
async def custom_docs(_=Depends(check_group)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Department Only API Docs",
        oauth2_redirect_url="/docs/oauth2-redirect"
    )

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(_=Depends(check_group)):
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_redirect():
    return {}

# 一般 API 不設限
@app.get("/api/hello")
async def hello():
    return {"msg": "hello"}