# 필드 조작하기
class Field():
    
    def insert_field(self, field_Name:str, Name:str): # 누름틀 필드 생성
        """
        누름틀 필드를 삽입하는 메서드입니다.

        Parameters:
            field_Name (str): 필드의 이름 
            Name (str): 필드의 내용 또는 방향 
        """
        # InsertFieldTemplate 액션의 기본값을 가져옵니다.
        self.hwp.HAction.GetDefault("InsertFieldTemplate", self.hwp.HParameterSet.HInsertFieldTemplate.HSet)
        
        # 필드 설정
        self.hwp.HParameterSet.HInsertFieldTemplate.TemplateDirection = Name  # 필드의 내용 또는 방향 설정
        self.hwp.HParameterSet.HInsertFieldTemplate.TemplateName = field_Name  # 필드의 이름 설정
        
        # 액션 실행하여 누름틀 필드 삽입
        self.hwp.HAction.Execute("InsertFieldTemplate", self.hwp.HParameterSet.HInsertFieldTemplate.HSet)


    def put_field_text(self, field_Name:str, Text:str):
        '지정한 필드에 넣고싶은 text를 넣습니다'
        return self.hwp.PutFieldText(f"{field_Name}", f"{Text}")  
    
    def get_field_list(self:None):
        '현재 한글파일에 생성된 모든 필드를 리스트로 보여줍니다.'
        return self.hwp.GetFieldList(1).split('')
    
    def get_field_text(self, field_Name:str):
        '선택된 필드의 text를 추출합니다.'
        return self.hwp.GetFieldText(f'{field_Name}')
    
    def goto_field(self, field_Name:str):
        '선택된 필드로 커서(캐럿)를 이동시킵니다.'
        return self.hwp.MoveToField(f'{field_Name}')
    
    def rename_field(self, oldname:str, newname:str):
        """
        지정한 필드의 이름을 바꾼다.
        예를 들어 oldname에 "title{{0}}\x02title{{1}}",
        newname에 "tt1\x02tt2로 지정하면 첫 번째 title은 tt1로, 두 번째 title은 tt2로 변경된다.
        oldname의 필드 개수와, newname의 필드 개수는 동일해야 한다.
        존재하지 않는 필드에 대해서는 무시한다.

        :param oldname:
            이름을 바꿀 필드 이름의 리스트. 형식은 PutFieldText와 동일하게 "\x02"로 구분한다.

        :param newname:
            새로운 필드 이름의 리스트. oldname과 동일한 개수의 필드 이름을 "\x02"로 구분하여 지정한다.

        :return: None

        :example:
            >>> hwp.create_field("asdf")  # "asdf" 필드 생성
            >>> hwp.rename_field("asdf", "zxcv")  # asdf 필드명을 "zxcv"로 변경
            >>> hwp.put_field_text("zxcv", "Hello world!")  # zxcv 필드에 텍스트 삽입
        """
        return self.hwp.RenameField(oldname=oldname, newname=newname)
    

    def delete_all_fields(self:None): # 한글 문서 내부의 모든 누름틀 필드 제거
        '''
        한글문서 내부의 모든 누름틀 필드를 제거한다.
        누름틀 필드에 삽입된 텍스트는 남는다.
        '''
        start_pos = self.get_pos()
        ctrl = self.hwp.HeadCtrl
        while ctrl:
            if ctrl.CtrlID == "%clk":
                self.hwp.DeleteCtrl(ctrl)
            ctrl = ctrl.Next
        for field in self.get_field_list():
            self.rename_field(field, "")
        return self.set_pos(*start_pos)
