from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, Field

# 앱
app = FastAPI() # app 이라는 이름의 FastAPI 객체 생성

# basemodel을 상속받아 데이터 모양 정의
class PostIn(BaseModel):
    # title은 문자형이고 최소 1글자, 최대 100글자
    title: str = Field(min_length=1, max_length=100)
    # content은 문자형이고 최소 1글자
    content: str = Field(min_length=1)

# 저장소
posts = []
next_id = 1

# 도우미 함수
def find_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
        raise HTTPException(status_code=404, detail="글이 없습니다")
    
# 경로 함수
@app.get("/") # 아래 함수를 "/" 경로에 GET 요청이 오면 실행
def home(): # 함수 정의
    # 돌려줄 내용을 딕셔너리로 만들어 FastAPI가 받아 JSON으로 변환
    return {"message": "안녕하세요"} 

@app.get("/posts") # 아래 함수를 /posts 경로에 GET 요청이 오면 실행
def list_posts():
    # 돌려줄 내용을 리스트로 만들어 FastAPI가 받아 JSON으로 변환
    return posts

@app.get("/posts/{post_id}") 
def get_post(post_id: int): 
    return find_post(post_id) 

# 경로 함수
# 아래 함수를 /posts 경로에 POST 요청이 오면 실행, 상태코드 201 반환
@app.post("/posts", status_code=201)
def create_post(body: PostIn): # body라는 이름의 PostIn 객체를 매개변수로 받음
    global next_id # next_id를 전역변수로 사용)
    # post라는 이름의 딕셔너리를 만들어 id, title, content를 저장
    post = {"id": next_id, "title": body.title, "content": body.content}
    posts.append(post) # post를 posts 리스트에 추가
    next_id += 1
    return post

@app.put("/posts/{post_id}") 
def update_post(post_id: int, body: PostIn):
    post = find_post(post_id)
    post["title"] = body.title
    post["content"] = body.content
    return post

@app.delete("posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    post = find_post(post_id)
    posts.remove(post)