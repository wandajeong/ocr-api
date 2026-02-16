import cv2
import numpy as np

def image_read(file_path):
    """cv2.imread 가 한국어명 파일을 읽어들이지 못하는 문제가 있어서 해당 함수 대체할 코드"""
    # np.fromfile을 통해 바이트로 읽어온 후 디코딩하여 한글 경로 문제 해결
    img_array = np.fromfile(file_path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img

def resize(img, n=3, interpolation=cv2.INTER_AREA):
    if (type(n) == int) or (type(n) == float):
        img = cv2.resize(
            img,
            (int(img.shape[1] * n), int(img.shape[0] * n)),
            interpolation=interpolation,
        )
    elif (type(n) == tuple) and (len(n) == 2):
        img = cv2.resize(img, n, interpolation=interpolation)
    return img

def crop_image(image, roi):
    """주어진 ROI를 사용하여 이미지의 일부분을 잘라내기"""
    src = image.copy()
    height, width = src.shape[:2]
    x, y, w, h = roi
    
    # 비율로 들어온 경우(0~1 사이) 픽셀 값으로 변환하는 로직 (코드 맥락상 추론)
    if w < 1:
        x = int(x * width)
        y = int(y * height)
        w = int(w * width)
        h = int(h * height)
    
    roi = [int(x), int(y), int(w), int(h)]
    img = src[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
    return img

def img_prepare(img):
    """pdf2image 의 결과물인 Pillow Image를 numpy array로 변환"""
    img = np.asarray(img)
    # 그레이스케일인 경우 RGB로 변환
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img

def img_preprocessing(img, dirty=True):
    """문서 이미지 대비 조절 및 노이즈 제거"""
    kernel = np.ones((2, 2), np.uint8)
    
    if dirty:
        # 1% 백분위수 기준으로 밝기 조정
        if np.percentile(img, 1) > 100:
            img = cv2.threshold(img, 200, 255, cv2.THRESH_TOZERO)[1]
        
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        img = cv2.threshold(img, 170, 255, cv2.THRESH_TOZERO)[1]
    else:
        pass
    return img

def closest_roi(target, img, method=cv2.TM_SQDIFF_NORMED):
    """대상 이미지에서 찾고자 하는 요소의 위치를 template matching을 통해 찾는 함수"""
    result = cv2.matchTemplate(target, img, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # TM_SQDIFF 계열은 최솟값이 가장 일치하는 지점임
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        MPx, MPy = min_loc
    else:
        MPx, MPy = max_loc
        
    trows, tcols = target.shape[:2]
    return (MPx, MPy, tcols, trows), (min_val, max_val)

def ask_coord(image, text="Select ROI"):
    """사용자에게 ROI를 선택할 수 있는 창을 띄워준 후, 선택한 ROI 반환"""
    height, width = image.shape[:2]
    cv2.namedWindow(text, cv2.WINDOW_NORMAL)
    coord = cv2.selectROIs(text, image, False, False)
    cv2.waitKey(0)
    
    if isinstance(coord, np.ndarray):
        coord = coord.tolist()
    
    cv2.destroyAllWindows()
    
    rel_coord = []
    for acoord in coord:
        x, y, w, h = acoord
        # 상대 좌표(0~1)로 변환
        rel_x = x / width
        rel_w = w / width
        rel_y = y / height
        rel_h = h / height
        rel_coord.append([rel_x, rel_y, rel_w, rel_h])
        
    return rel_coord

def mask_alittle(target_img, roi, alpha):
    x, y, w, h = roi
    shapes = np.zeros_like(target_img, np.uint8)
    cv2.rectangle(shapes, (x, y), (x + w, y + h), (255, 255, 255), cv2.FILLED)
    mask = shapes.astype(bool)
    
    # 지정한 영역에 투명도를 적용하여 덮어쓰기
    target_img[mask] = cv2.addWeighted(target_img, alpha, shapes, 1 - alpha, 0)[mask]
    return target_img

def alignImages(im1, im2, max_matches=1000, good_match=0.15):
    # Convert images to grayscale
    im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    
    # Detect ORB features and compute descriptors
    orb = cv2.ORB_create(max_matches)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)
    
    # Match features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)
    
    # Sort matches by score
    matches = sorted(matches, key=lambda x: x.distance, reverse=False)
    
    # Remove not so good matches
    numGoodMatches = int(len(matches) * good_match)
    matches = matches[:numGoodMatches]
    
    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)
    
    for i, match in enumerate(matches):
        points1[i] = keypoints1[match.queryIdx].pt
        points2[i] = keypoints2[match.trainIdx].pt
        
    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
    
    if h is None:
        im1Reg = im1
    else:
        # Use homography to warp image
        height, width = im2.shape[:2]
        im1Reg = cv2.warpPerspective(im1, h, (width, height))
        
    return im1Reg, h

def erase_lines(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Gaussian blur to improve edge detection
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold the image
    binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Perform edge detection
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)
    
    # Perform Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    
    if (lines is None) or (len(lines) == 0):
        pass
    else:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 흰색으로 선을 그려서 지움
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
    return img
