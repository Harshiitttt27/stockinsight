from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from api.models import Prediction
from api.ml import predict_stock_and_generate_plots

class Command(BaseCommand):
    help = "Run prediction for a given ticker or all tickers in system"

    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Stock ticker (e.g. TSLA)')
        parser.add_argument('--all', action='store_true', help='Predict for all distinct tickers used before')

    def handle(self, *args, **options):
        if options['all']:
            tickers = Prediction.objects.values_list('ticker', flat=True).distinct()
            if not tickers:
                raise CommandError("No previous tickers found to predict.")
        elif options['ticker']:
            tickers = [options['ticker'].upper()]
        else:
            raise CommandError("Specify either --ticker <TICKER> or --all")

        # Use first superuser as dummy for CLI predictions
        try:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not user:
                raise CommandError("No users found to associate predictions with.")
        except Exception as e:
            raise CommandError(f"User error: {e}")

        for ticker in tickers:
            try:
                self.stdout.write(f"Predicting for: {ticker}")
                price, mse, rmse, r2, plot1, plot2 = predict_stock_and_generate_plots(ticker)

                Prediction.objects.create(
                    user=user,
                    ticker=ticker,
                    next_day_price=price,
                    mse=mse,
                    rmse=rmse,
                    r2=r2,
                    plot_1=plot1.replace(settings.MEDIA_ROOT + '/', ''),
                    plot_2=plot2.replace(settings.MEDIA_ROOT + '/', '')
                )

                self.stdout.write(self.style.SUCCESS(f"✓ {ticker} prediction saved."))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"✗ Failed for {ticker}: {e}"))
