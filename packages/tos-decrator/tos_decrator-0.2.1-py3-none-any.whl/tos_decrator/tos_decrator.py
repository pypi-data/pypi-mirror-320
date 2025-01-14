import functools
import tos
import io
import os
import tempfile
import logging
import pickle
def init_client(ak,sk,endpoint="tos-cn-beijing.volces.com"):
    # ak = os.getenv('TOS_ACCESS_KEY')
    # sk = os.getenv('TOS_SECRET_KEY')
    # ak = 'AKLTMjdmYjhhNjA0OTE5NGYxMThjZTZiZTdmZmIyNmI2Y2M'
    # sk = 'TUdNNVlUZ3dPVFptTmpRNE5ETTFZamsyWldNMFlXRTBOMlprWm1JeE5UUQ=='
    # your endpoint 和 your region 填写Bucket 所在区域对应的Endpoint。# 以华北2(北京)为例，your endpoint 填写 tos-cn-beijing.volces.com，your region 填写 cn-beijing。
    # endpoint = endpoint
    region = "cn-beijing"
    client = tos.TosClientV2(ak, sk, endpoint, region)
    return client
def tos_process_decorator(bucket_name="mm-data-general-model-v1"):
    logger = logging.getLogger(__name__)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(client,object_key, suffix=None, tos_prefix=None, output_key=None,upload=True,*args, **kwargs):
            # 初始化TOS客户端
            # client = init_client()
            
            # 从TOS读取文件到临时文件
            try:
                object_stream = io.BytesIO(client.get_object(bucket_name, object_key).read())
                
                # 调用原始函数，传入临时文件路径
                result = func(object_stream, *args, **kwargs)

                if upload:
                    if not isinstance(result, io.BytesIO):
                        result_bytes = io.BytesIO()
                        pickle.dump(result, result_bytes)
                        result = result_bytes
                    try:
                        with tempfile.NamedTemporaryFile(suffix=suffix,delete=True) as tmp_result_file:
                            # result.save(tmp_result_file)
                            tmp_result_file.write(result.getvalue())
                            client.put_object_from_file(bucket_name, os.path.join(tos_prefix, output_key), tmp_result_file.name)
                        logger.info(f'Successful process and upload {object_key}')
                        return result
                    except:
                        logger.error('fail with upload error!! please check passing paras！')
                else:
                    #不进行上传，直接返回函数处理结果
                    return result
            except tos.exceptions.TosClientError as e:
                logger.error('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
            except tos.exceptions.TosServerError as e:
                logger.error('fail with server error, code: {}'.format(e.code))
                logger.error('error with request id: {}'.format(e.request_id))
                logger.error('error with message: {}'.format(e.message))
                logger.error('error with http code: {}'.format(e.status_code))
                logger.error('error with ec: {}'.format(e.ec))
                logger.error('error with request url: {}'.format(e.request_url))
            except Exception as e:
                logger.error('fail with unknown error: {}'.format(e))
        return wrapper
    return decorator

if __name__ =="__main__":
    # 使用装饰器
    from PIL import Image
    @tos_process_decorator()
    def process_data(local_file_path, *args, **kwargs):
        # 这里进行数据处理
        # 假设处理后的数据保存在临时文件中
        test_png = Image.open(local_file_path)
        return test_png

    # 调用装饰过的函数
    object_key = 'rendering/cam15/02a5ac47db6e09d5235bea600068dd0cdad7682dfa265d7052c247e3d21abf88/View5_SceneDepth.png'
    tos_prefix = 'rendering/cam15/02a5ac47db6e09d5235bea600068dd0cdad7682dfa265d7052c247e3d21abf88/'
    output_key = 'View5_SceneDepth_test.png'
    suffix = '.png'
    process_data(object_key=object_key,suffix=suffix, tos_prefix=tos_prefix, output_key=output_key)