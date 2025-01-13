class keyboard:
    
    # 우연히 찾은 문단 컨트롤 방법
    def line_down(self):
        '현재 캐럿위치의 문단을 한칸 내린다. 단축키는 alt + shift + down'
        self.hwp.HAction.Run("EditParaDown")
    def line_up(self):
        '현재 캐럿위치의 문단을 한칸 올린다. 단축키는 alt + shift + up'
        self.hwp.HAction.Run("EditParaUp")
    

    @property
    def ctrl_c(self):
        'ctrl + c와 같은 기능이다.'
        self.hwp.HAction.Run("Copy")
    
    @property
    def ctrl_v(self):
        'ctrl + v와 같은 기능이다.'
        self.hwp.HAction.Run("Paste")

    @property
    def ctrl_x(self):
        'ctrl + x(잘라내기)와 같은 기능이다.'
        self.hwp.HAction.Run("Cut")

    @property
    def delete(self):
        'Delete 키와 같은 기능이다.'
        self.hwp.HAction.Run("Delete")

    @property
    def backspace(self):
        'Backspace 키와 같은 기능이다.'
        self.hwp.HAction.Run("DeleteBack")
    
    @property
    def enter(self):
        '''
        글자 한 문단을 내려간다.
        '''
        self.hwp.HAction.Run("BreakPara")

    @property
    def esc(self):
        '''
        esc와 같은 기능이다.
        설정된 select를 푼다.
        '''
        self.hwp.HAction.Run("Cancel")
    
    @property
    def left(self):
        '''
        왼쪽으로 한칸 캐럿 이동
        '''
        self.hwp.HAction.Run("MoveLeft")
    
    @property
    def right(self):
        '''
        오른쪽으로 한칸 캐럿 이동
        '''
        self.hwp.HAction.Run("MoveRight")
    
    @property
    def up(self):
        '''
        위쪽으로 한칸 캐럿 이동
        '''
        self.hwp.HAction.Run("MoveUp")
    
    @property
    def down(self):
        '''
        아래쪽으로 한칸 캐럿 이동
        '''
        self.hwp.HAction.Run("MoveDown")

    @property
    def shift_left(self):
        '''
        왼쪽으로 한칸 블록선택
        '''
        self.hwp.HAction.Run("MoveSelLeft")
    
    @property
    def shift_right(self):
        '''
        오른쪽으로 한칸 블록선택
        '''
        self.hwp.HAction.Run("MoveSelRight")
    
    @property
    def shift_up(self):
        '''
        위쪽으로 한칸 블록선택
        '''
        self.hwp.HAction.Run("MoveSelUp")
    
    @property
    def shift_down(self):
        '''
        아래쪽으로 한칸 블록선택
        '''
        self.hwp.HAction.Run("MoveSelDown")

    @property
    def ctrl_left(self):
        '''
        한 단어 앞으로 이동
        '''
        self.hwp.HAction.Run("MovePrevWord")
    
    @property
    def ctrl_right(self):
        '''
        한 단어 뒤로 이동
        '''
        self.hwp.HAction.Run("MoveNextWord")
    