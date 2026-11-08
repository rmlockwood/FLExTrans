// App.xaml.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17.1 - 11/8/26 - Ron Lockwood
//  Sets the UI language chosen in the app's Language menu item, or the phone's, before the page is built.
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. The app: one window holding MainPage in a NavigationPage, for the title bar and its menu.
//
// OVERVIEW (AI generated, then edited)
//
// The app itself: one window holding MainPage in a NavigationPage, which gives it the title bar and its ⋮ menu. It also owns the UI language, since that has to be set before any page is built.
//
// THE UI LANGUAGE
//
// The page's words come from AppResources (Resources/Strings/AppResources*.resx), which .NET picks by CultureInfo.CurrentUICulture. Left alone that's the phone's language, but phones before
// Android 13 have no setting to give one app another language, so the page's Language menu item lets the user choose one of UILanguages.All, or "Same as the phone". The choice is kept in
// Preferences ("uiLanguage": a code, or empty for the phone's) and set here, in the constructor, before CreateWindow() builds the page. SetUILanguage() changes it while the app runs; the page
// then builds itself again (MainPage.OnLanguageClicked), since its XAML read its words once, when it was built.
//
// Only the UI culture changes. Dates and numbers keep the phone's own regional format (CurrentCulture), which the user chose in the phone's settings and may differ from the UI language.
//
// TRAPS
//
//  - phoneUICulture is captured when the class is first used, before anything changes the culture, so "Same as the phone" can go back to it after another language was chosen.
//  - AppResources.Culture is what really sets the language: every AppResources lookup uses it, on any thread. CultureInfo.CurrentUICulture alone isn't enough, because SetUILanguage() is
//    called from an async handler (MainPage.OnLanguageClicked), and .NET undoes a culture set inside an async method when the method returns. The page built inside the handler came out in
//    the new language, but every later handler (the language-pair list, say) ran in the old one again. CurrentUICulture and DefaultThreadCurrentUICulture are still set, for anything else
//    in .NET that looks up text by the UI culture.
//  - A saved code that is no longer a UI language (one dropped from UILanguages.py) counts as "Same as the phone".
//
// CODE STRUCTURE
//
// The constructor sets the saved UI language; CreateWindow() builds the window and the page. UILanguageCode is the choice; SetUILanguage() saves and sets a new one, and ApplyUILanguage() sets it.
//

using System.Globalization;

using FTtranslator.Phone.Resources.Strings;

namespace FTtranslator.Phone;

public partial class App : Application
{
	// Where the chosen UI language is remembered
	const string UILanguageKey = "uiLanguage";

	// The phone's UI language, before any choice changed it. See TRAPS above.
	static readonly CultureInfo phoneUICulture = CultureInfo.CurrentUICulture;

	// The chosen UI language's code, or empty for the phone's
	public static string UILanguageCode { get; private set; } = "";

	public App()
	{
		ApplyUILanguage(Preferences.Default.Get(UILanguageKey, ""));
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		return new Window(new NavigationPage(new MainPage()));
	}

	// Remember a new UI language (a code from UILanguages.All, or empty for the phone's) and set it. Pages built from now on use it.
	public static void SetUILanguage(string code)
	{
		Preferences.Default.Set(UILanguageKey, code);
		ApplyUILanguage(code);
	}

	// Set the UI language for AppResources, this thread and threads started later. See TRAPS above.
	static void ApplyUILanguage(string code)
	{

		if (!UILanguages.All.Any(language => language.Code == code))
		{
			code = "";
		}

		UILanguageCode = code;
		CultureInfo culture = code.Length > 0 ? new CultureInfo(code) : phoneUICulture;
		AppResources.Culture = culture;
		CultureInfo.CurrentUICulture = culture;
		CultureInfo.DefaultThreadCurrentUICulture = culture;
	}
}
