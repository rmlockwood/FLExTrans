// SceneDelegate.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/9/26
//
// Version 3.17 - 11/9/26 - Ron Lockwood
//  Initial version. iOS's scene delegate: apps built with the iOS 27 SDK must use UIKit's scene life cycle or iOS won't launch them.
//
// The window lives in a UIKit scene. Info.plist's UIApplicationSceneManifest names this class for MAUI's default scene configuration, and MAUI's MauiUISceneDelegate does the rest (it
// creates the window from App.CreateWindow), so nothing needs overriding here. Without the manifest and this class, iOS stops the app at start-up with "UIScene life cycle is required for
// apps built with this SDK".
//

using Foundation;

namespace FTtranslator.Phone;

[Register("SceneDelegate")]
public class SceneDelegate : MauiUISceneDelegate
{
}
