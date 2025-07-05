import glob
import os

from django.conf import settings
from django.shortcuts import render

from api.ml import predict_stock_and_generate_plots

from django.conf import settings

def dashboard_view(request):
    context = {
        'MEDIA_URL': settings.MEDIA_URL, 
    }

    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper().strip()
        if not ticker:
            context["error"] = "Ticker symbol is required."
        else:
            try:
                price, mse, rmse, r2, plot1_path, plot2_path = predict_stock_and_generate_plots(ticker)

                plot1_rel = os.path.relpath(plot1_path, settings.MEDIA_ROOT)
                plot2_rel = os.path.relpath(plot2_path, settings.MEDIA_ROOT)

                context.update({
                    "ticker": ticker,
                    "price": price,
                    "mse": mse,
                    "rmse": rmse,
                    "r2": r2,
                    "plot1_url": settings.MEDIA_URL + plot1_rel.replace('\\', '/'),
                    "plot2_url": settings.MEDIA_URL + plot2_rel.replace('\\', '/'),
                })

            except Exception as e:
                context["error"] = str(e)

    # Load existing plots
    import glob
    plot_files = glob.glob(os.path.join(settings.MEDIA_ROOT, 'plots', '*_plot*.png'))
    plot_urls = [settings.MEDIA_URL + os.path.relpath(path, settings.MEDIA_ROOT).replace('\\', '/') for path in plot_files]
    context["existing_plots"] = plot_urls

    return render(request, "dashboard.html", context)
