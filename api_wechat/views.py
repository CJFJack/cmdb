# -*- encoding: utf-8 -*-

from rest_framework.views import APIView
from api_wechat.WXBizMsgCrypt import WXBizMsgCrypt
from api_wechat.utils import workflow_approve_receive_wx_callback
from api_wechat.utils import workflow_handle_receive_wx_callback
from django.http import JsonResponse, HttpResponse
from cmdb.logs import WXMsgReceiveLog
from urllib.parse import unquote_plus
import xml.etree.cElementTree as ET
import sys
import json

sToken = "EOnpuMnGoBvlhhmOLkNOewe"
sEncodingAESKey = "nORkk9tpFgeJnVlLFgwTL8LWV9KNf5l9bHoUeYn58m4"
sCorpID = "ww07fea2b7f6cafa5b"


class WechatMsgReceiveAPI(APIView):
    """微信信息回调接口"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """用于接收微信服务器测试连接，确保cmdb接口正常可用"""
        log = WXMsgReceiveLog()
        try:
            raw_data = request.query_params
            log.logger.info('测试与微信服务器建立链接: {}'.format(json.dumps(raw_data)))
            wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
            sVerifyMsgSig = raw_data.get('msg_signature', None)
            sVerifyTimeStamp = raw_data.get('timestamp', None)
            sVerifyNonce = raw_data.get('nonce', None)
            sVerifyEchoStr = raw_data.get('echostr', None)
            ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
            sEchoStr = str(sEchoStr, encoding="utf8")
            if ret != 0:
                log.logger.error('ERR: VerifyURL ret: {} echistr: {}'.format(str(ret), str(sEchoStr)))
            else:
                log.logger.info('解密成功，字符串 {}'.format(sEchoStr))
            return HttpResponse(sEchoStr)
        except Exception as e:
            msg = str(e)
            log.logger.error('解密失败，原因: {}'.format(msg))

    def post(self, request):
        """用于接收微信服务器将用户发送给微信应用的消息回调给cmdb的请求"""
        log = WXMsgReceiveLog()
        try:
            raw_data = request.query_params
            log.logger.info('收到微信回调: {}'.format(json.dumps(raw_data)))
            wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
            sReqMsgSig = raw_data.get('msg_signature', None)
            sReqTimeStamp = raw_data.get('timestamp', None)
            sReqNonce = raw_data.get('nonce', None)
            sReqData = request.body
            sReqData = str(sReqData, encoding="utf8")
            ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
            if ret != 0:
                log.logger.error("ERR: DecryptMsg ret: {}".format(str(ret)))
            else:
                log.logger.info('解密消息成功，任务卡片内容: {}'.format(sMsg))
                xml_tree = ET.fromstring(sMsg)
                """判断是否任务卡片点击事件，不是则忽略"""
                try:
                    Event = xml_tree.find("Event").text
                except Exception as e:
                    pass
                else:
                    if Event == 'taskcard_click':
                        FromUserName = xml_tree.find("FromUserName").text.lower()
                        log.logger.info('审批人: {}'.format(FromUserName))
                        TaskId = xml_tree.find("TaskId").text
                        log.logger.info('任务id: {}'.format(TaskId))
                        EventKey = xml_tree.find("EventKey").text
                        if EventKey in ('yes', 'no'):
                            log.logger.info('审批结果: {}'.format(EventKey))
                            """审批工单"""
                            workflow_approve_receive_wx_callback(TaskId, EventKey, FromUserName)
                        if EventKey == 'is_handle':
                            log.logger.info('处理结果: {}'.format(EventKey))
                            """更新工单处理状态"""
                            workflow_handle_receive_wx_callback(TaskId, EventKey, FromUserName)
                        if EventKey == 'is_purchase':
                            log.logger.info('处理结果: {}'.format(EventKey))
                            """更新工单已构买状态"""
                            workflow_handle_receive_wx_callback(TaskId, 'is_handle', FromUserName)
        except Exception as e:
            log.logger.error(str(e))
        finally:
            return HttpResponse('')
