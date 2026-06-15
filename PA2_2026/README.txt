2022007329 김규현

[작성/수정한 파일 | Files made or changed]
- SimpleScene.py   : 본 과제에서 직접 작성/수정한 파일 (TODO 부분 구현)

[그대로 사용한 스켈레톤 파일 | Unchanged skeleton files]
- OBJ.py           : OBJ 메쉬 로더/렌더러 (수정 안 함)
- Ray.py           : Ray / Plane / normalize 유틸 (수정 안 함)
- cow.obj          : 소 삼각형 메쉬
- camera.obj       : 카메라 모델
- bricks.bmp       : 바닥 텍스처

[실행 방법 | How to run]
1. 필요한 패키지 설치: python3, pillow(PIL), glfw, numpy, PyOpenGL
       pip install pillow glfw numpy PyOpenGL
2. 작업 디렉터리에서 실행 (cow.obj 가 같은 폴더에 있어야 함):
       python SimpleScene.py

[조작 방법 | Controls]
- space / c          : 카메라 시점 전환
- 소 위에서 L-click   : 소를 집는다(pick)
- L-drag (상하)       : 집은 소의 높이(y)를 조절한다  (vertical dragging)
- 마우스 이동         : 소를 바닥(xz 평면) 위에서 수평 이동시킨다 (horizontal positioning)
- L-click             : 현재 위치에 제어점을 지정하고, 그 자리에 소를 복제한다
- 제어점 6개를 모두 지정하면 cyclic B-spline 트랙을 따라 소가 3바퀴 주행한다
- 주행이 끝나면 다시 초기 모드(소가 커서를 따라가는 모드)로 돌아간다

[구현 내용 | Implementation notes]
- 제어점 UI            : 클릭 시 cow2wld 행렬을 controlPoints 에 저장하고 display() 에서
                         각 제어점 위치에 소를 복제 렌더링한다.
- 수직/수평 드래그     : onMouseDrag() 의 V_DRAG 는 시선 벡터에 수직인 평면과의 교차로
                         y 성분만 갱신하고, H_DRAG 는 바닥(y=상수) 평면 교차로 xz 를 갱신한다.
- Cyclic B-spline      : splinePoint() 에서 균일 3차 B-spline basis 행렬(BSPLINE_M)을 사용하며,
                         4개의 연속 제어점을 순환(cyclic) 인덱싱하여 평가하는 근사(approximating)
                         스플라인이다.
- yaw / pitch          : cowFrame() 에서 스플라인의 접선(tangent)을 진행 방향(front)으로 삼아
                         cross product 로 직교 프레임을 구성한다. 접선이 수직 성분을 포함하므로
                         yaw(진행 방향)와 pitch(오르막에서 위를 보는 회전)가 동시에 반영된다.
