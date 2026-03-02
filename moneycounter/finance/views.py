from finance.serializers import (
    CategorySerializer,
    TransactionSerializer,
    AccountSerializer,
    CurrencySerializer,
    FinancialGoalSerializer,
    VoiceTransactionSerializer,
    TextTransactionSerializer
)
from finance.filters import TransactionFilter
from rest_framework import viewsets, status
from finance.models import Category, Transaction, Account, Currency, FinancialGoal
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from django.db.models import Q, Sum
from ai_services.tasks import process_voice_transaction_task, process_text_transaction_task
from datetime import datetime, timedelta

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    Users can only see their own categories or global ones.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns categories belonging to the user and global categories."""
        return self.queryset.filter(Q(user=self.request.user) | Q(user__isnull=True))

    def perform_create(self, serializer):
        """Assigns the category to the current user upon creation."""
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows transactions to be viewed or edited.
    Provides filtering and ordering out of the box.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = TransactionFilter
    ordering_fields = ['date', 'amount_original']
    ordering = ['-date', '-id']

    def get_queryset(self):
        """Returns transactions belonging exclusively to the current user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assigns the transaction to the current user upon creation."""
        serializer.save(user=self.request.user)


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user accounts to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns accounts belonging to the current user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assigns the account to the current user upon creation."""
        serializer.save(user=self.request.user)


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currencies to be viewed or edited.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]


class FinancialGoalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows financial goals to be viewed or edited.
    """
    queryset = FinancialGoal.objects.all()
    serializer_class = FinancialGoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns financial goals for the current user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assigns the financial goal to the current user upon creation."""
        serializer.save(user=self.request.user)


class AnalyticsView(APIView):
    """
    API view for retrieving user's analytics (income and expenses grouped by category).
    Supports optional 'start_date' and 'end_date' query parameters.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handles GET request to fetch analytics within the given date range."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = Transaction.objects.filter(user=request.user)

        if start_date:
            try:
                # Ensure it's treated correctly as date
                dt_start = datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(date__gte=dt_start)
            except ValueError:
                return Response({"error": "Invalid start_date format (YYYY-MM-DD required)"}, status=400)
        
        if end_date:
            try:
                # Include the full end day by adding 1 day and using less than
                dt_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                queryset = queryset.filter(date__lt=dt_end)
            except ValueError:
                return Response({"error": "Invalid end_date format (YYYY-MM-DD required)"}, status=400)

        # Expenses
        expenses_qs = queryset.filter(category__type=Category.Type.EXPENSE)
        expenses_report = (
            expenses_qs.values('category__name')
            .annotate(total=Sum('amount_original'))
            .order_by('-total')
        )

        # Income
        income_qs = queryset.filter(category__type=Category.Type.INCOME)
        income_report = (
            income_qs.values('category__name')
            .annotate(total=Sum('amount_original'))
            .order_by('-total')
        )
        
        return Response({
            "expenses": expenses_report,
            "income": income_report
        })


class VoiceTransactionView(APIView):
    """
    API view for submitting a voice transaction audio file to be processed asynchronously.
    """
    parser_classes = (MultiPartParser,)  # Для загрузки файлов

    def post(self, request):
        """Handles POST request, saves the uploaded audio file temporarily, and starts the processing task."""
        serializer = VoiceTransactionSerializer(data=request.data)

        if serializer.is_valid():
            # 1. Сохраняем файл временно на диск
            audio_file = request.FILES["audio_file"]
            file_name = default_storage.save(f"tmp/{audio_file.name}", audio_file)
            file_path = default_storage.path(file_name)

            # 2. Запускаем Celery задачу в фоновом режиме
            process_voice_transaction_task.delay(
                user_id=request.user.id,
                file_path=file_path,
                account_id=serializer.validated_data["account_id"],
                chat_id=serializer.validated_data.get("chat_id")
            )

            return Response(
                {"detail": "Обработка голоса началась в фоновом режиме."},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TextTransactionView(APIView):
    """
    API view for submitting a raw text transaction description to be processed asynchronously.
    """
    def post(self, request):
        """Handles POST request and starts the text processing task."""
        serializer = TextTransactionSerializer(data=request.data)

        if serializer.is_valid():
            process_text_transaction_task.delay(
                user_id=request.user.id,
                text=serializer.validated_data["text"],
                account_id=serializer.validated_data["account_id"],
                chat_id=serializer.validated_data.get("chat_id")
            )

            return Response(
                {"detail": "Обработка текста началась в фоновом режиме."},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)