import cv2
import numpy as np

#Vẽ bounding box
def bounding_box(x1,y1,x2,y2,img, thick=3):
    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), thick)
    return img
    
def XY4_to_XYXY(bboxes):
    new_bboxes=[]
    for box in bboxes:
        x1=box[0][0]
        y1=box[0][1]
        x2=box[2][0]
        y2=box[2][1]
        new_bboxes.append([x1,y1,x2,y2])
    return new_bboxes

def arrange_bbox(bboxes):
    n = len(bboxes)
    xcentres = [(b[0] + b[2]) // 2 for b in bboxes]
    ycentres = [(b[1] + b[3]) // 2 for b in bboxes]
    heights = [abs(b[1] - b[3]) for b in bboxes]
    width = [abs(b[2] - b[0]) for b in bboxes]

    def is_top_to(i, j):
        result = (ycentres[j] - ycentres[i]) > ((heights[i] + heights[j]) / 3)
        return result

    def is_left_to(i, j):
        return (xcentres[i] - xcentres[j]) > ((width[i] + width[j]) / 3)

    # <L-R><T-B>
    # +1: Left/Top
    # -1: Right/Bottom
    g = np.zeros((n, n), dtype='int')
    for i in range(n):
        for j in range(n):
            if is_left_to(i, j):
                g[i, j] += 10
            if is_left_to(j, i):
                g[i, j] -= 10
            if is_top_to(i, j):
                g[i, j] += 1
            if is_top_to(j, i):
                g[i, j] -= 1
    return g


def arrange_row(bboxes=None, g=None, i=None, visited=None):
    if visited is not None and i in visited:
        return []
    if g is None:
        g = arrange_bbox(bboxes)
    if i is None:
        visited = []
        rows = []
        for i in range(g.shape[0]):
            if i not in visited:
                indices = arrange_row(g=g, i=i, visited=visited)
                visited.extend(indices)
                rows.append(indices)
        return rows
    else:
        indices = [j for j in range(g.shape[0]) if j not in visited]
        indices = [j for j in indices if abs(g[i, j]) == 10 or i == j]
        indices = np.array(indices)
        g_ = g[np.ix_(indices, indices)]
        order = np.argsort(np.sum(g_, axis=1))
        indices = indices[order].tolist()
        indices = [int(i) for i in indices]
        return indices

def split_row(rows,bboxes,ratio=0.5):
    xcentres = [(b[0] + b[2]) // 2 for b in bboxes]
    x1x2= [ [b[0],b[2]] for b in bboxes]  
    mean_hight=np.mean( [abs(b[1] - b[3]) for b in bboxes]) 
    new_rows=[]

    # print("mean_hight: ",mean_hight)
    max_width= ratio*mean_hight
    for row in rows:
        new_row=[row[0]]
        for i in range(1,len(row)):
            if abs(x1x2[row[i]][0]-x1x2[row[i-1]][1]) > max_width:
                new_rows.append(new_row)
                new_row=[row[i]]
            else:
                new_row.append(row[i])
        new_rows.append(new_row)
    
    return new_rows