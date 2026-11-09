// AppDelegate.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/9/26
//
// Version 3.17 - 11/9/26 - Ron Lockwood
//  Initial version. iOS's application delegate, which hands start-up to MauiProgram, as MainApplication does on Android.
//

using Foundation;

namespace FTtranslator.Phone;

[Register("AppDelegate")]
public class AppDelegate : MauiUIApplicationDelegate
{

	protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
}
