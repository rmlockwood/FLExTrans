// TraceView.xaml.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. A translation's trace section, shared by the current translation and the history's cards.
//

namespace FTtranslator.Phone;

public partial class TraceView : ContentView
{
	public TraceView()
	{
		InitializeComponent();
	}

	// Tapping "Trace" opens or closes the details
	void OnToggleTapped(object? sender, TappedEventArgs e)
	{

		if (BindingContext is TranslationItem item)
		{
			item.IsTraceOpen = !item.IsTraceOpen;
		}
	}

	// Tapping a section's heading folds it open or closed; the heading's gesture passes its Section
	void OnSectionTapped(object? sender, TappedEventArgs e)
	{

		if (e.Parameter is Section section)
		{
			section.IsOpen = !section.IsOpen;
		}
	}
}
