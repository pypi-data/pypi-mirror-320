class select:
    
    @property
    def copy(self):
        'ctrl + c와 같은 기능이다.'
        self.hwp.HAction.Run("Copy")
    
    @property
    def paste(self):
        'ctrl + v와 같은 기능이다.'
        self.hwp.HAction.Run("Paste")

    def select_ctrl(self, target_index:int=1):
        """
        번호에 맞는 컨트롤을 선택한다.
        """
        # 컨트롤정의 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        ctrls_dict = {}
        index = 1

        # 딕셔너리로 저장
        while ctrl:

            ctrls_dict[index] = ctrl.GetAnchorPos(0)
            index += 1
            ctrl = ctrl.Next

        # 번호가 존재하는지 확인 후 선택
        selected_pos = ctrls_dict.get(target_index)
        if selected_pos:
            # Move to the selected position
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            
            return True
        else:
            # Target index does not exist
            return False
    
    def select_picture(self, target_index:int=1):
        """
        번호에 맞는 그림을 선택한다.
        """
        # 컨트롤정의 및 그림저장 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        picture_dict = {}
        index = 1

        # 그림 객체만 딕셔너리로 저장
        while ctrl:
            if ctrl.UserDesc == '그림':
                picture_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 그림 번호가 존재하는지 확인 후 선택
        selected_pos = picture_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            
            return True
        else:
            # Target index does not exist
            return False

    def select_table(self, target_index:int=1):
        """
        번호에 맞는 표를 선택한다.
        """
        # 컨트롤정의 및 그림저장 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        picture_dict = {}
        index = 1

        # 그림 객체만 딕셔너리로 저장
        while ctrl:
            if ctrl.UserDesc == '표':
                picture_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 그림 번호가 존재하는지 확인 후 선택
        selected_pos = picture_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            
            return True
        else:
            # Target index does not exist
            return False