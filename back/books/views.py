from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404 , get_list_or_404
from rest_framework.response import Response
from .models import Account_book, Account_book_data, Budget, Schedule
from cards.models import Category, Credit_cards, Check_cards
from cards.serializers import RecommendCheckCard, RecommendCreditCard

from .serializers import AccountBookCalendar, AccountBookDataSerializer,BudgetPostPutSerializer, BudgetSerializer, ScheduleSerializer, AccountBookSerializer, MonthlyDataSerializer,AnalysisTimeSerialzer,CategoryExpenseSerializer , EvaluationSerializer
from django.db import transaction

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import requests
import time
import uuid
import json
import os

import math 


from django.db.models import Q, Sum

from datetime import datetime
from collections import defaultdict


from openai import OpenAI

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.cache import CacheBackedEmbeddings

from rest_framework.pagination import LimitOffsetPagination

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar(request):  # 캘린더 페이지
    try:
        account_book = get_object_or_404(Account_book, user_id=request.user) 
    except:  # 가계부 인스턴스 없으면 생성
        account_book = Account_book.objects.create(user_id=request.user)
    
    serializer = AccountBookSerializer(account_book)
    return Response(serializer.data)

# 하루치 결제 데이터 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def day(request):
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == "GET":
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        day = request.query_params.get('day') 

        account_book_data = Account_book_data.objects.filter(
            account_book_id=account_book.pk,
            day = int(day),
            month = int(month),
            year = int(year)
            )
        serializer = AccountBookCalendar(account_book_data,many=True)
        return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated]) 
# def page_data(request):
#     account_book = get_object_or_404(Account_book, user_id=request.user)
#     if request.method == "GET":
#         year= datetime.now().year
#         account_book_data = Account_book_data.objects.filter(
#             account_book_id=account_book.pk,
#             year=year
#         ).order_by('-month', 'day')  # month 내림차순, day 오름차순

#         paginator = LimitOffsetPagination()
#         result_page = paginator.paginate_queryset(account_book_data, request)
#         serializer = AccountBookCalendar(result_page, many=True)
        
#         return paginator.get_paginated_response(serializer.data)


# 한달 내역 데이터 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def month(request):
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == "GET":
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        account_book_data = Account_book_data.objects.filter(
            account_book_id=account_book.pk,
            month = int(month),
            year = int(year)
            )
        serializer = AccountBookCalendar(account_book_data,many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def year(request):
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == "GET":
        year= datetime.now().year
        account_book_data = Account_book_data.objects.filter(
            account_book_id=account_book.pk,
            year=year
        ).order_by('-month', 'day')  # month 내림차순, day 오름차순
        serializer = AccountBookCalendar(account_book_data,many=True)
        return Response(serializer.data)


# 고정 스케줄 조회 삽입 수정 삭제
@api_view(['GET','POST','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def schedule(request):
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == 'GET':
        schedules = Schedule.objects.filter(
            account_book_id = account_book
        )
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        name = request.data.get('name')
        day = request.data.get('day')
        value = request.data.get('value')
        category_id = request.data.get('category_id')
        is_income = request.data.get('is_income')
        sehedule = {
            'account_book_id':account_book.pk,
            'name': name,
            'day': int(day),
            'value': int(value),
            'category_id': int(category_id),
            'is_income': is_income
        }
        serializer =ScheduleSerializer(data=sehedule)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error":"schedule_id is required for update."},status=status.HTTP_400_BAD_REQUEST)
        
        schedule = get_object_or_404(Schedule,account_book_id = account_book,schedule_id=schedule_id)

        serializer = ScheduleSerializer(schedule, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error": "schedule_id is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        schedule = get_object_or_404(Schedule,account_book_id = account_book,schedule_id=schedule_id)
        schedule.delete()
        return Response({"message": f"Schedule with id {schedule_id} has been deleted."}, status=status.HTTP_204_NO_CONTENT)


# 예산 조회 삽입 및 수정 메서드
@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def budget(request):
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == 'GET':
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        # print(month)
        month=int(month)
        year=int(year)
        try:
            budget = get_object_or_404(Budget, account_book_id=account_book.pk)
        except:
            budget = Budget.objects.create(month=month,year=year,value=0,account_book_id=account_book)
        serializer = BudgetSerializer(budget)

        return Response(serializer.data)

    elif request.method == 'POST':
        # print(account_book.pk)
        year = request.data.get('year')
        month = request.data.get('month')
        value = request.data.get('value')

        budget = {
            'account_book_id': account_book.pk,
            'month': int(month),
            'value': int(value),
            'year' : int(year),
        }
        serializer =BudgetPostPutSerializer(data=budget)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        budget_id = request.data.get('budget_id')
        if not budget_id:
            return Response({"error":"budget_id is required for update."},status=status.HTTP_400_BAD_REQUEST)
        
        budget = get_object_or_404(Budget,account_book_id = account_book,budget_id=budget_id)

        serializer = BudgetSerializer(budget, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 여러 지출 내역 추가, 수정 삭제
@api_view(['POST','DELETE'])
@permission_classes([IsAuthenticated])
def write_account_data_list(request): 
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    if request.method == 'POST':
        with transaction.atomic():
            data = request.data
            if isinstance(data, list):
                response = []
                for item in data:
                    serializer = AccountBookDataSerializer(data={**item, 'account_book_id':account_book.pk})
                    if serializer.is_valid():
                        serializer.save()
                        response.append(serializer.data)
                    else:
                        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Invalid data format, expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)
            
    elif request.method == 'DELETE':
        with transaction.atomic():
            data = request.data
            # print(data)
            if isinstance(data,list) and all(isinstance(id, str) for id in data):
                try:
                    account_book_data = Account_book_data.objects.filter(
                        account_book_data_id__in=data,
                        account_book_id=account_book
                    )
                    cnt = account_book_data.count()
                    if cnt == 0:
                        return Response({"message": "No matching records found to delete."}, status=status.HTTP_404_NOT_FOUND)
                    
                    account_book_data.delete()
                    return Response({'message': f'Deleted {cnt} items.'}, status=status.HTTP_204_NO_CONTENT)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid data format, expected a list of integer IDs."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def write_account_data(request): # 단일 지출
    account_book = get_object_or_404(Account_book, user_id=request.user) 
    
    if request.method == 'POST':
        year = request.data.get('year')
        month = request.data.get('month')
        account = request.data.get('account')
        day = request.data.get('day')
        is_income = request.data.get('is_income')
        payment = request.data.get('payment')
        store = request.data.get('store')
        category_id = request.data.get('category_id')
        memo = request.data.get('memo')

        data = {
            "year" : int(year),
            "month" : int(month),
            "account" : int(account),
            "day" : int(day),
            "is_income" : is_income,
            "payment" : payment,
            "store" : store,
            "category_id" : int(category_id),
            "memo": memo
        }
        # print(data)

        serializer = AccountBookDataSerializer(data={**data, 'account_book_id':account_book.pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # PUT 요청 - 단일 지출 수정
    elif request.method == 'PUT':
        # year = request.data.get('year')
        # month = request.data.get('month')
        # account = request.data.get('account')
        # day = request.data.get('day')
        # is_income = request.data.get('is_income')
        # payment = request.data.get('payment')
        # store = request.data.get('store')
        # category_id = request.data.get('category_id')

        # data = {
        #     "year" : int(year),
        #     "month" : int(month),
        #     "account" : int(account),
        #     "day" : int(day),
        #     "is_income" : is_income,
        #     "payment" : payment,
        #     "store" : store,
        #     "category_id" : int(category_id)
        # }
        account_book_data_id = request.data.get('account_book_data_id')
        if not account_book_data_id:
            return Response({"error": "account_book_data_id is required for update."}, status=status.HTTP_400_BAD_REQUEST)

        # 수정할 인스턴스 조회
        account_book_data_instance = get_object_or_404(Account_book_data, account_book_data_id=account_book_data_id, account_book_id=account_book)

        # 수정 데이터 적용
        serializer = AccountBookDataSerializer(account_book_data_instance, data=request.data, partial=True)  # 일부 필드만 수정 가능
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE 요청 - 단일 지출 삭제
    elif request.method == 'DELETE':
        account_book_data_id = request.data.get('account_book_data_id')
        if not account_book_data_id:
            return Response({"error": "account_book_data_id is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        # 삭제할 인스턴스 조회
        account_book_data_instance = get_object_or_404(Account_book_data, account_book_data_id=account_book_data_id, account_book_id=account_book)
        account_book_data_instance.delete()
        return Response({"message": f"Account book data with id {account_book_data_id} has been deleted."}, status=status.HTTP_204_NO_CONTENT)

def category_ask(userInput):
    media_path = os.path.join(settings.BASE_DIR, 'static','category_input.json')
    try:
        with open(media_path, 'r', encoding='utf-8') as file:
            category_data = json.load(file)

        categories_summary = "\n".join([f"{key} (ID: {value['category_id']}): {', '.join(value['kinds'])}" for key, value in category_data.items()])
        
        # print(categories_summary)
        OPENAI_API_KEY =settings.MY_OPENAI_API_KEY

        client = OpenAI(api_key=OPENAI_API_KEY)
        # 페르소나 지정 및 기존 대화 내용 저장
        conversation_history = [
            {"role": "system", "content": "당신은 사용자가 입력한 영수증의 구매 내역 카테고리를 알려주는 프로그램이야."},
            {"role": "system", "content": "내가 정한 카테고리는 총 27개야 "},
            {"role": "system", "content": f'The categories are: {categories_summary}'},
            {"role": "system", "content": "답변은 내가 정해준 카테고리 중 너가 생각하는 카테고리를 선택해서 category_id 가 몇번인지 알려주면 출력해줘"},
            {"role": "system", "content": "어딘지 모르겠으면 기타로 분류해야하니까 출력값은 '25'로 하면 돼"},
            {"role": "system", "content": "만약 카테고리가 푸드이면 숫자 '7'만 출력하고 다른 말은 하면 안돼."},
            {"role": "system", "content": "어떤 설명도 추가하지 말고, 숫자만 출력해야 돼."},
        ]

        conversation_history.append(
            {
                "role": "user",
                "content": f"{userInput}",
            }
        )

        response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",  # 사용하려는 모델 (필수 지정)
        messages=conversation_history,  # 대화 메시지 목록 (필수 지정)
        max_tokens=500,  # 생성될 응답의 최대 토큰 수 (값의 범위: 1~모델 마다 최대값 ex> gpt-3.5-turbo: 16,385 tokens)
        temperature=0.7,  # 확률 분포 조정을 통한 응답의 다양성 제어 (값의 범위: 0~2)
        top_p=0.9,  # 누적 확률 값을 통한 응답의 다양성 제어 (값의 범위: 0~1)
        n=1,  # 생성할 응답 수 (1이상의 값)
        seed=1000 # 랜덤 씨드 값
        )
        # 응답 출력
        for response in response.choices :
            # print('result',response.message.content)
            return int(response.message.content)
    except Exception as e:
        # print(f"Error: OpenAI API call failed - {e}")
        return 25


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receipt(request): # 영수증 OCR
    if request.method == 'POST':
        # 요청의 헤더를 확인
        # print(f"Request Headers: {request.headers}")
        
        # 파일을 가져와서 확인
        file = request.FILES.get('image')
        if not file:
            # print("No file uploaded.")
            return Response({'error': 'No file uploaded'}, status=400)

        # 파일 정보 출력
        # print(f"File name: {file.name}")
        # print(f"File size: {file.size}")
        # print(f"File content type: {file.content_type}")
        
        # FileSystemStorage를 사용하여 media 폴더에 파일 저장
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        headers = {
            'X-OCR-SECRET': settings.NAVER_OCR_API_KEY,
        }        
        message = {
            'version':'V2',
            'requestId':str(uuid.uuid4()),
            'timestamp':int(time.time()*1000),
            'images':[
                {
                    'format':file.name.split('.')[-1],
                    'name':'sample_image'
                }
            ]
        }

        try:
            # 요청 데이터 만들기
            with open(file_path, 'rb') as img_file:
                files = {
                    'message': (None, json.dumps(message), 'application/json'),
                    'file': (filename, img_file, file.content_type)
                }
                # 네이버 OCR API 요청
                response = requests.post(settings.NAVER_OCR_URL, headers=headers, files=files)
                response_data = response.json()  # JSON 응답 파싱

                # 응답 데이터를 JSON 파일로 저장
                # json_filename = f"ocr_response_{uuid.uuid4().hex}.json"
                # json_file_path = os.path.join(settings.MEDIA_ROOT, json_filename)
                # with open(json_file_path, 'w', encoding='utf-8') as json_file:
                #     json.dump(response_data, json_file, ensure_ascii=False, indent=4)

            # API 요청 성공 시 응답 반환
            if response.status_code == 200:
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                try:
                    store =response_data['images'][0]['receipt']['result']['storeInfo']['name']['text']
                except:
                    store = ''
                
                try:
                    year =response_data['images'][0]['receipt']['result']['paymentInfo']['date']['formatted']['year']
                except:
                    year =0

                try:
                    month =response_data['images'][0]['receipt']['result']['paymentInfo']['date']['formatted']['month']
                except:
                    month = 0

                try:
                    day =response_data['images'][0]['receipt']['result']['paymentInfo']['date']['formatted']['day']
                except:
                    day = 0

                try:
                    account =response_data['images'][0]['receipt']['result']['totalPrice']['price']['formatted']['value']
                except:
                    account = 0

                AI_input =f'{store}에서 총 결제 금액:{account}원 결제 했어.'

                try:
                    subResults =response_data['images'][0]['receipt']['result']['subResults'][0]['items']
                    memo=''
                    for item in subResults:
                        try:
                            menu= item['name']['formatted']['value']
                            memo += f'{menu}'
                        except:
                            pass
                        try:
                            cnt = item['count']['formatted']['value']
                            memo += f'({cnt}개)'
                        except:
                            pass
                        try:
                            price = item['price']['price']['formatted']['value']
                            memo += f'{price}원'
                        except:
                            pass
                        try:
                            unitPrice = item['price']['unitPrice']['formatted']['value']
                            memo += f'개당 {unitPrice}원'
                        except:
                            pass
                        memo +=', \n'
                    AI_input += f'상세 내역은 {memo}이야'
                    # print(memo)
                except:
                    memo=''

                category_id=category_ask(AI_input)
                try:
                    int(category_id)
                except:
                    category_id=25

                data ={
                    "store":store,
                    "year":year,
                    "month":month,
                    "day":day,
                    "account":account,
                    "is_income":False,
                    "payment":'카드', 
                    "category_id":category_id,
                    "memo":memo

                }

                return Response({'message': 'File uploaded and OCR processed successfully', 'data': data}, status=200)
            else:
                # 에러 응답 시
                return Response({'error': 'Failed to process OCR', 'details': response_data}, status=response.status_code)

        except Exception as e:
            return Response({'error': 'Internal server error', 'details': str(e)}, status=500)
    return Response({'error': 'Invalid request method'}, status.HTTP_405_METHOD_NOT_ALLOWED )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calender_data(request): 
    account_book = get_object_or_404(Account_book, user_id=request.user)

    if request.method == 'GET':
        # 요청 파라미터 유효성 검사
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))

            if not (1 <= month <= 12):
                return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)

        except (ValueError, TypeError):
            return Response({'error': 'Invalid year or month parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # 한달 데이터 모으기
        month_data = Account_book_data.objects.filter(
            year=year,
            month=month,
            account_book_id=account_book.pk
        )

        # 한 달 전체 수익 및 지출 합산
        total_income = month_data.filter(is_income=True).aggregate(total=Sum('account'))['total'] or 0
        total_expenditure = month_data.filter(is_income=False).aggregate(total=Sum('account'))['total'] or 0

        # 날짜별 그룹화 후 수익 및 지출 합산
        day_data = []
        grouped_data = month_data.values('day').annotate(
            income=Sum('account', filter=Q(is_income=True)),
            expenditure=Sum('account', filter=Q(is_income=False))
        )

        for day_entry in grouped_data:
            day_data.append({
                'day': day_entry['day'],
                'income': day_entry['income'] or 0,
                'expenditure': day_entry['expenditure'] or 0,
            })

        # 오름차순 정렬 추가
        day_data = sorted(day_data, key=lambda x: x['day'])

        # 시리얼라이저 사용하여 데이터 응답
        monthly_data = {
            'total_income': total_income,
            'total_expenditure': total_expenditure,
            'day_data': day_data
        }

        serializer = MonthlyDataSerializer(monthly_data)
        return Response(serializer.data)

    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# import pprint 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_category(request):
    account_book = get_object_or_404(Account_book, user_id=request.user)

    if request.method == 'GET':
        # 요청 파라미터 유효성 검사
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))
            if not (1 <= month <= 12):
                return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid year or month parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # 한달 데이터 모으기
        month_data = Account_book_data.objects.filter(
            year=year,
            month=month,
            account_book_id=account_book.pk,
            is_income = False
        )

        # 카테고리 id 별로 account 합쳐야함
        # 카테고리별 소비 금액 합계 계산
        category_expenses = month_data.values('category_id').annotate(total_amount=Sum('account'))
        # pprint.pprint(category_expenses)
        category_summary = []
        for category in category_expenses:
            category_id = category['category_id']
            total_amount = category['total_amount']

            details = month_data.filter(category_id=category_id).values(
                'day', 'account', 'payment', 'store', 'memo'
            ).order_by('day')

            # 요약 및 세부 내역 추가
            category_summary.append({
                'category_id': category_id,
                'total_amount': total_amount,
                'details': list(details)
            })
        # print(category_summary)
        serializer =CategoryExpenseSerializer(category_summary, many=True)

        return Response(serializer.data)
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

def evaluation(month_data,birth,budget):
    try:
        # print(budget.value)
        user_input=f'이번달 나의 예산은 {budget}원이야. 나는 이번 한달 동안'
        total=0
        for data in month_data:
            total +=data['total_amount']
            user_input += f'{data["category_name"]}에 {data["total_amount"]}원, '

        # print('totol',total)
        user_input +=f'총 {total}원을 사용했어 내 소비 습관 어때?? '


        OPENAI_API_KEY =settings.MY_OPENAI_API_KEY

        client = OpenAI(api_key=OPENAI_API_KEY)
        # 페르소나 지정 및 기존 대화 내용 저장
        conversation_history = [
            {"role": "system", "content": "너는 사용자의 소비 내역을 바탕으로 사용자가 올바른 소비를 하고 있는지 평가하는 사용자 지갑 지킴이야."},
            {"role": "system", "content": "만약 사용자의 소비 내역이 문제가 있어 보인다면 과격한 표현을 사용해가며 사용자가 경각심을 느낄 수 있도록 해줘야해."},
            {"role": "system", "content": "사용자의 나이대와 비슷한 다른 사람들과 마음껏 비교해도 괜찮아."},
            {"role": "system", "content": "만약 사용자가 소비를 올바르게 잘 하고 있다면 칭찬해 줘."},
            {"role": "system", "content": "250자 이내로 부탁해."},
        ]

        conversation_history.append(
            {
                "role": "user",
                "content": f"나는 {birth}에 태어났어",
            }
        )
        conversation_history.append(
            {
                "role": "user",
                "content": f"{user_input}",
            },
        )

        response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",  # 사용하려는 모델 (필수 지정)
        messages=conversation_history,  # 대화 메시지 목록 (필수 지정)
        max_tokens=1000,  # 생성될 응답의 최대 토큰 수 (값의 범위: 1~모델 마다 최대값 ex> gpt-3.5-turbo: 16,385 tokens)
        temperature=0.7,  # 확률  분포 조정을 통한 응답의 다양성 제어 (값의 범위: 0~2)
        top_p=0.6,  # 누적 확률 값을 통한 응답의 다양성 제어 (값의 범위: 0~1)
        n=1,  # 생성할 응답 수 (1이상의 값)
        seed=1000 # 랜덤 씨드 값
        )
        # 응답 출력
        for response in response.choices :
            return response.message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evaluation_gpt(request):
    account_book = get_object_or_404(Account_book, user_id=request.user)
    if request.method == 'GET':
        year= datetime.now().year
        month = datetime.now().month

        # 한달 데이터 모으기
        month_data = Account_book_data.objects.filter(
            year=year,
            month=month,
            account_book_id=account_book.pk,
            is_income = 'False',
        )

        if month_data.count() <= 10:
            comment ='데이터가 적어서 평가를 제공할 수 없습니다.'
            return Response({'comment': comment}, status=status.HTTP_200_OK)

        # 카테고리 id 별로 account 합쳐야함
        # 카테고리별 소비 금액 합계 계산
        category_expenses = month_data.values('category_id').annotate(total_amount=Sum('account'))

        category_summary = []
        for category in category_expenses:
            category_id = category['category_id']
            total_amount = category['total_amount']
            category_instance = get_object_or_404(Category, pk=category_id)
            category_name = category_instance.category_name
            # 요약 및 세부 내역 추가
            # print('category_name',category_name)
            # print('total_amount',total_amount)
            category_summary.append({
                'category_name':category_name,
                'total_amount': total_amount,
            })
        try :
            budget = Budget.objects.get(account_book_id=account_book.pk)
        except:
            budget =0

        sorted_category_summary = sorted(category_summary, key=lambda x: x
        ['total_amount'], reverse=True)
        # pprint.pprint(sorted_category_summary)
        # print(request.user.birth)
        comment =evaluation(sorted_category_summary,request.user.birth,budget)
        data = {'comment':comment}
        serializer = EvaluationSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_time(request):
    account_book = get_object_or_404(Account_book, user_id=request.user)

    if request.method == 'GET':
        # 요청 파라미터 유효성 검사
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))

            if not (1 <= month <= 12):
                return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)

        except (ValueError, TypeError):
            return Response({'error': 'Invalid year or month parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        month_age_1 = month-1
        month_age_2 = month-2

        # 1개월 전과 2개월 전의 month와 year 계산
        if month == 1:
            month_age_1 = 12
            year_age_1 = year - 1
            month_age_2 = 11
            year_age_2 = year - 1
        elif month == 2:
            month_age_1 = 1
            year_age_1 = year
            month_age_2 = 12
            year_age_2 = year - 1
        else:
            month_age_1 = month - 1
            year_age_1 = year
            month_age_2 = month - 2
            year_age_2 = year

        # 한달 데이터 모으기
        month_data = Account_book_data.objects.filter(
            year=year,
            month=month,
            is_income=False,
            account_book_id=account_book.pk,
        )

        # 11월 고정 지출 결제 내역
        schedules = month_data.filter(is_schedule=True)

        schedules = schedules.order_by('day')

        total_schedules= schedules.aggregate(total=Sum('account'))['total'] or 0

        # 1달 전 지출 
        total_expenditure_age_1 = Account_book_data.objects.filter(
            year=year_age_1,
            month=month_age_1,
            is_income=False,
            account_book_id=account_book.pk
        ).aggregate(total=Sum('account'))['total'] or 0

        # 2달전 지출
        total_expenditure_age_2 = Account_book_data.objects.filter(
            year=year_age_2,
            month=month_age_2,
            is_income=False,
            account_book_id=account_book.pk
        ).aggregate(total=Sum('account'))['total'] or 0

        # 현재 달 지출
        total_expenditure= month_data.filter(is_income=False).aggregate(total=Sum('account'))['total'] or 0
        
        # 현재달 하루 총 지출
        day_data = []
        grouped_data = month_data.values('day').annotate(
            expenditure=Sum('account', filter=Q(is_income=False))
        )

        for day_entry in grouped_data:
            day_data.append({
                'day': day_entry['day'],
                'expenditure': day_entry['expenditure'] or 0,
            })

        # 오름차순 정렬 추가
        day_data = sorted(day_data, key=lambda x: x['day'])

        # 주별 지출은 어떻게 구해야 할까?
        
        week_data = defaultdict(int)

        for day_entry in grouped_data:
            day = day_entry['day']
            expenditure = day_entry['expenditure'] or 0

            week_number = math.ceil(day/7) 

            # 주별 지출 합산
            week_data[week_number]  += expenditure

        # 주별 지출 리스트로 변환 및 정렬
        weekly_data = [{'week': week,'expenditure':expenditure} for week, expenditure in week_data.items()]
        weekly_data = sorted(weekly_data,key=lambda x: x['week'])

        # 응답 데이터 생성
        analysis_data = {
            'total_expenditure': total_expenditure,
            'total_expenditure_age_1': total_expenditure_age_1,
            'total_expenditure_age_2': total_expenditure_age_2,
            'total_schedules':total_schedules,
            'day_data': day_data,
            'weekly_data': weekly_data,
            'schedules':schedules,
        }

        # 시리얼라이저를 사용하여 응답 반환
        serializer = AnalysisTimeSerialzer(analysis_data)


        return Response(serializer.data)
    
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_cards(request):
    account_book = get_object_or_404(Account_book, user_id=request.user)

    if request.method == 'GET':
        # 요청 파라미터 유효성 검사
        try:
            year = datetime.now().year
            month = datetime.now().month
            if not (1 <= month <= 12):
                return Response({'error': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid year or month parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # 한달 데이터 모으기
        month_data = Account_book_data.objects.filter(
            year=year,
            month=month,
            account_book_id=account_book.pk,
            is_income = False
        )

        # 카테고리 id 별로 account 합쳐야함
        # 카테고리별 소비 금액 합계 계산
        category_expenses = month_data.values('category_id').annotate(total_amount=Sum('account'))

        category_summary = []
        for category in category_expenses:
            category_id = category['category_id']
            total_amount = category['total_amount']
            category_instance = get_object_or_404(Category, pk=category_id)
            category_name = category_instance.category_name
            # 요약 및 세부 내역 추가
            category_summary.append({
                'category_name':category_name,
                'total_amount': total_amount,
            })
        sorted_category_summary = sorted(category_summary, key=lambda x: x['total_amount'], reverse=True)
        
        category_list=[]
        for data in sorted_category_summary:
            category_list.append(data['category_name'])
        
        # print(category_list)
        # OpenAI API 키 설정
        # OpenAI Embeddings 및 캐싱 설정
        embeddings = OpenAIEmbeddings(openai_api_key=settings.MY_OPENAI_API_KEY)
        cache_dir = "./embedding_cache"
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

        # Django 프로젝트 경로에 맞게 설정
        credit_store_dir = os.path.join(settings.BASE_DIR, 'books', 'faiss_vector_store_creidt')
        check_store_dir = os.path.join(settings.BASE_DIR, 'books', 'faiss_vector_store_check')

        credit_vectorstore = FAISS.load_local(credit_store_dir, embeddings=cached_embeddings,allow_dangerous_deserialization=True)
        check_vectorstore =FAISS.load_local(check_store_dir, embeddings=cached_embeddings,allow_dangerous_deserialization=True)

        credit_retriever = credit_vectorstore.as_retriever(search_kwargs={"k": 20})
        check_retriever = check_vectorstore.as_retriever(search_kwargs={"k": 20})

        credit_ids={}
        check_ids={}
        
        for category in category_list:
            weight = len(category_list) - category_list.index(category)
            credit_results=credit_retriever.invoke(category)
            check_results =check_retriever.invoke(category)
            for result in credit_results:
                content = result.page_content
                # 문자열을 "Card ID :" 기준으로 나눈 후 두 번째 부분에서 공백을 제거하고 추가
                card_id = content.split("Card ID :")[1].strip()
                if card_id in credit_ids:
                    credit_ids[card_id] += weight
                else:
                    credit_ids[card_id] = weight
            for result in check_results:
                content = result.page_content
                # 문자열을 "Card ID :" 기준으로 나눈 후 두 번째 부분에서 공백을 제거하고 추가
                card_id = content.split("Card ID :")[1].strip()
                if card_id in check_ids:
                    check_ids[card_id] += weight
                else:
                    check_ids[card_id] = weight

        # credit_ids 딕셔너리에서 상위 3개의 항목을 가져오기
        top_3_credit_ids = sorted(credit_ids.items(), key=lambda x: x[1], reverse=True)[:3]

        # check_ids 딕셔너리에서 상위 3개의 항목을 가져오기
        top_3_check_ids = sorted(check_ids.items(), key=lambda x: x[1], reverse=True)[:3]

        # ID만 따로 리스트 형태로 추출하고 싶다면 다음과 같이 할 수 있습니다.
        credits_list = [card_id for card_id, weight in top_3_credit_ids]
        check_list = [card_id for card_id, weight in top_3_check_ids]

        # 체크카드 정보 조회
        check_cards = Check_cards.objects.filter(check_card_id__in=check_list)

        # 신용카드 정보 조회
        credit_cards = Credit_cards.objects.filter(credit_card_id__in=credits_list)

        credit_cards_serializer = RecommendCreditCard(credit_cards,many=True)
        check_cards_serializer = RecommendCheckCard(check_cards, many=True)

        response_data = {
            'credit_cards': credit_cards_serializer.data,
            'check_cards': check_cards_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
