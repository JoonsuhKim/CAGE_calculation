class BubbleNode:
    def __init__(self, ISO, x_axis, y_axis, CLS, CAGE=None):
        self.ISO = ISO          # 국가코드
        self.x_axis = x_axis    # x값: 1인당 GDP
        self.y_axis = y_axis    # y값: 1인당 소비량
        self.CLS = CLS          # 고전적 매력도 파라미터
        self.CAGE = CAGE        # CAGE 매력도 파라미터
        self.next = None        # 다음 노드 링크