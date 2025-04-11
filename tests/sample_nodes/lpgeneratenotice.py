from datetime import datetime
from langpipe import LPBaseInvoker

class LPGenerateNotice(LPBaseInvoker):
    """
    generate notice something like:
    您好，这里是[随岳监控中心]，
    2024年10月31日17:07接[12122]上报：[徐广高速][429公里][广州方向]，发现[散落物]，[有很多散落的衣物等垃圾在路面上]，请前往处理。
    """

    def __init__(self, name, param_keys=['上报人', '接收人', '事发高速', '事发位置', '事发方向', '事件名称', '事件描述']) -> None:
        super().__init__(name)
        self.__param_keys = param_keys
        self.__param_values = []
        self.__notice_template = """您好，这里是{0},{1}接{2}上报：{3}{4}{5}，发现{6}，{7}，请前往处理。"""
        self.__generated_notice = None
    
    def _invoke(self, lpdata) -> None:
        extracted_params = lpdata.get('global_vars', {}).get('extracted_params', {})
        for key in self.__param_keys:
            self.__param_values.append(extracted_params.get(key, ''))
        
        if all(item != '' for item in self.__param_values) and len(self.__param_values) == 7:
            values = []
            values.append(self.__param_values[1])
            values.append(datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
            values.append(self.__param_values[0])
            values.extend(self.__param_values[2:])
            self.__generated_notice = self.__notice_template.format(*values)

    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__param_keys'] = self.__param_keys
        record['local_vars']['param_values'] = self.__param_values
        record['local_vars']['__notice_template'] = self.__notice_template

        # update global variables
        if self.__generated_notice is not None:
            lpdata['final_out'] = self.__generated_notice
            lpdata['global_vars']['generated_notice'] = self.__generated_notice       
    
