from django.contrib import messages
from django.shortcuts import redirect, render

from . import analytics
from .forms import ImportForm
from .importers import import_trading212_csv
from .models import CashMovement, Trade


def dashboard(request):
    trades = Trade.objects.all()
    cash = CashMovement.objects.all()
    context = {
        "summary": analytics.summary(trades, cash),
        "by_ticker": analytics.realised_by_ticker(trades),
        "by_month": analytics.realised_by_month(trades),
        "recent": trades[:20],
    }
    return render(request, "trades/dashboard.html", context)


def import_csv(request):
    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data["file"].read().decode("utf-8-sig").splitlines()
            result = import_trading212_csv(text, form.cleaned_data["account"])
            messages.success(
                request,
                f"Imported {result.trades_created} trades and {result.cash_created} cash rows "
                f"({result.skipped_duplicates} duplicates skipped).",
            )
            return redirect("dashboard")
    else:
        form = ImportForm()
    return render(request, "trades/import.html", {"form": form})
