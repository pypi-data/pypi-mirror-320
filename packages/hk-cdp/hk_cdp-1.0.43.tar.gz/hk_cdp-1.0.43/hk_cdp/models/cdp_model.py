class ListKey():
    """
    @description: 队列key
    """
    @classmethod
    def tt_history_member_list(self, store_id, is_check = False):
        """
        :description: 抖音历史会员队列
        :param store_id: 店铺标识
        :param is_check: is_check
        :return str
        :last_editors: HuangJianYi
        """
        prefix = "tt_history_member_list"
        if is_check == True:
            return f"{prefix}:check:{store_id}"
        return f"{prefix}:{store_id}"
    

    @classmethod
    def member_merge_list(self, merge_type, store_id, is_check = False):
        """
        :description: one_id合并队列
        :param merge_type: 合并类型，'omid' 或 'telephone'
        :param store_id: 店铺标识
        :param is_check: is_check
        :return str
        :last_editors: HuangJianYi
        """
        prefix = f"member_{merge_type}_merge_list"
        if is_check == True:
            return f"{prefix}:check:{store_id}"
        return f"{prefix}:{store_id}"
    

    @classmethod
    def register_member_list(self, store_id, is_check = False):
        """
        :description: one_id合并队列
        :param store_id: 店铺标识
        :param is_check: is_check
        :return str
        :last_editors: HuangJianYi
        """
        prefix = "register_member_list"
        if is_check == True:
            return f"{prefix}:check:{store_id}"
        return f"{prefix}:{store_id}"

   
    @classmethod
    def member_mask_telephone_list(self, business_id, is_check = False):
        """
        :description: one_id合并队列
        :param business_id: 商家标识
        :param is_check: is_check
        :return str
        :last_editors: HuangJianYi
        """
        prefix = "member_mask_telephone_list"
        if is_check == True:
            return f"{prefix}:check:businessid_{business_id}"
        return f"{prefix}:businessid_{business_id}"