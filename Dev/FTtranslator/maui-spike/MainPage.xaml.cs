namespace HcSpike;

public partial class MainPage : ContentPage
{
	public MainPage()
	{
		InitializeComponent();
	}

	bool hasRun;

	// Run once on start, so a run can be driven entirely over adb (install, launch, read logcat)
	protected override void OnAppearing()
	{
		base.OnAppearing();

		if (!hasRun)
		{
			hasRun = true;
			OnRunClicked(null, EventArgs.Empty);
		}
	}

	async void OnRunClicked(object? sender, EventArgs e)
	{
		RunButton.IsEnabled = false;
		SummaryLabel.Text = "Parsing...";

		try
		{
			HcRunResult result = await HcRunner.RunAsync();
			SummaryLabel.Text = $"{result.WordCount} words: {result.WithAnalyses} with analyses, {result.WithErrors} with errors.\n"
				+ $"Load {result.LoadSeconds:F2} s, parse {result.ParseSeconds:F2} s.\nSaved to {result.OutputPath}";
			OutputLabel.Text = result.Lines;

			// For adb logcat, so the run can be checked without reading the screen
			Console.WriteLine($"HCSPIKE {SummaryLabel.Text.Replace('\n', ' ')}");
		}
		catch (Exception ex)
		{
			SummaryLabel.Text = "Failed: " + ex.GetType().Name + ": " + ex.Message;
			OutputLabel.Text = ex.ToString();
			Console.WriteLine("HCSPIKE FAILED " + ex);
		}
		finally
		{
			RunButton.IsEnabled = true;
		}
	}
}
