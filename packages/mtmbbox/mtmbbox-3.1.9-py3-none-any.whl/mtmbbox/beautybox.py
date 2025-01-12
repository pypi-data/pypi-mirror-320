from .request import BBoxRequest
from .constants import HOST_DATA, HOST_CHAT_PIC


class BeautyBox:
    HOST_DATA = HOST_DATA[0]
    HOST_CHAT_PIC = HOST_CHAT_PIC

    @staticmethod
    def user_login(
        crypto, auths: dict, captcha="9d184bc8a496a52cfdc2594f85f2639a", points="26,37", rtype="a", **kwargs
    ):
        url = f"https://{BeautyBox.HOST_DATA}/auth/json"
        data = {
            "x5": auths["username"],
            "x7": auths["password"],
            "xi": captcha,
            "xj": points,
            "x1": auths["certcode"],
            "x0": rtype,
        }
        resp: dict = BBoxRequest.request("POST", url, data, crypto, 1, **kwargs)
        return resp

    @staticmethod
    def user_bind(cypto, token, auths, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/user/cert/bound/json"
        data = {"p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def user_unbind(cypto, token, auths, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/user/cert/unbound/json"
        data = {"p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def user_assets(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/user/expire/info/json"
        resp = BBoxRequest.request("GET", url, {}, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_market_orders_list(cypto, token, rtype, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/json"
        data = {"t": rtype}
        resp = BBoxRequest.request("GET", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_seller_orders_list(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/seller/json"
        resp = BBoxRequest.request("GET", url, {}, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_seller_orders_place(cypto, token, auths, order_type: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/seller/new/json"
        data = {"t": order_type, "p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_seller_orders_confirm(cypto, token, auths, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/seller/confirm/json?id={order_id}"
        data = {"p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_seller_orders_dispute(cypto, token, auths, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/dispute/json?id={order_id}"
        data = {"p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_buyer_orders_list(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/buyer/json"
        resp = BBoxRequest.request("GET", url, {}, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_buyer_orders_place(cypto, token, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/buyer/place/json"
        data = {"id": order_id}
        resp = BBoxRequest.request("GET", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_buyer_orders_payment(cypto, token, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/buyer/payment/json"
        data = {"id": order_id}
        resp = BBoxRequest.request("GET", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def txn_buyer_orders_cancel(cypto, token, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/transaction/buyer/nopayment/json"
        data = {"id": order_id}
        resp = BBoxRequest.request("GET", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def reg_market_orders_list(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/registration/json"
        resp = BBoxRequest.request("GET", url, {}, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def reg_seller_orders_list(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/registration/seller/json"
        data = {"x0": "a"}
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data.update({"x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]})
        # data.update({"x2": "", "x3": 13, "x4": ""})
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def reg_seller_orders_place(cypto, token, auths, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/registration/seller/json"
        data = {"xa": 0, "x9": auths["paypwd"], "x0": "b"}
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data.update({"x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]})
        # data.update({"x2": "", "x3": 13, "x4": ""})
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def reg_seller_orders_confirm(cypto, token, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/registration/seller/json"
        data = {"x6": order_id, "x0": "d"}
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data.update({"x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]})
        # data.update({"x2": "", "x3": 13, "x4": ""})
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def reg_seller_orders_dispute(cypto, token, auths, order_id: int, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/registration/seller/json"
        data = {"x6": order_id, "x9": auths["paypwd"], "x0": "e"}
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data.update({"x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]})
        # data.update({"x2": "", "x3": 13, "x4": ""})
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def chat_list(cypto, token, chat_id, page=1, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/chat/show/json"
        data = {"id": chat_id, "page": page}
        resp = BBoxRequest.request("GET", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def chat_send(cypto, token, chat_id, content, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/chat/new/json"
        if isinstance(content, bytes):
            image = content.decode()
            data = {"chat_id": chat_id, "image": image, "target": 0}
        else:
            data = {"chat_id": chat_id, "content": content, "target": 0}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def chat_pic(cypto, chat_id, **kwargs):
        url = f"https://{BeautyBox.HOST_CHAT_PIC}/chat"
        data = {"id": chat_id}
        resp = BBoxRequest.request("GET", url, data, cypto, 6, **kwargs)
        return resp

    @staticmethod
    def user_payment_list(cypto, token, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/user/payment/json?ac=list"
        resp = BBoxRequest.request("GET", url, {}, cypto, 1, token=token, **kwargs)
        return resp

    @staticmethod
    def user_payment_edit(cypto, token, auths, payid, payurl, **kwargs):
        url = f"https://{BeautyBox.HOST_DATA}/user/payment/json?ac=edit&id={payid}"
        data = {"account": payurl, "p": auths["paypwd"]}
        resp = BBoxRequest.request("POST", url, data, cypto, 1, token=token, **kwargs)
        return resp
