// Program.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/9/26
//
// Version 3.17 - 11/9/26 - Ron Lockwood
//  Initial version. iOS's entry point: starts UIKit with AppDelegate.
//

using UIKit;

namespace FTtranslator.Phone;

public class Program
{

	// The app's entry point on iOS. UIApplication.Main never returns; AppDelegate takes over from here.
	static void Main(string[] args)
	{
		UIApplication.Main(args, null, typeof(AppDelegate));
	}
}
