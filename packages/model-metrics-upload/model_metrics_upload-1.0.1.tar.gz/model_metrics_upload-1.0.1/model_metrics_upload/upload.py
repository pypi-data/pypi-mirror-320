
import requests
import os


def upload(metric_name="", metric_value="", metric_explain=""):
    token = os.getenv('EVALUATION_TOKEN')
    evaluation_id = os.getenv('EVALUATION_JOB_ID')
    hook_svc = os.getenv('HOOK_URL')
    if token == "":
        print("get token failed!")
        return False

    if evaluation_id == "":
        print("get evaluation_id failed!")
        return False

    if hook_svc == "":
        print("get hook_url failed!")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if not metric_name:
        print("metric name is required!")
        return False

    if not metric_value:
        print("metric value is required!")
        return False

    json_data = {
        "evaluationId": evaluation_id,
        "columnKey": metric_name,
        "columnExplain": metric_explain,
        "contents": metric_value
    }

    response = requests.post(hook_svc, headers=headers, json=json_data, verify=False)

    if response.status_code == 200:
        json_response = response.json()
        # print(json_data)  # 打印响应的 JSON 数据
        if json_response.get('success'):
            return True
        else:
            print(f"Failed. msg: {json_response['error']['message']}")
            return False
    else:
        print(f"Failed. Status code: {response.status_code}")
        return False


if __name__ == "__main__":
    upload("ceshi", "测试", "一个测试指标")
