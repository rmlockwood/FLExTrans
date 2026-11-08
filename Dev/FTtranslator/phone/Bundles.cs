// Bundles.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17.2 - 11/7/26 - Ron Lockwood
//  The export time (ExportedText) and the bad-zip errors are in the UI language (AppResources).
//
// Version 3.17.1 - 11/7/26 - Ron Lockwood
//  Reads whether the source and target languages are right to left (sourceRightToLeft, targetRightToLeft) from the manifest.
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. The bundles on the phone: the ones built into the app and the ones added or updated from a zip.
//
// OVERVIEW (AI generated, then edited)
//
// A bundle is one language pair's translation data (export-bundle's Output\ftt_bundle folder). The phone can hold several and the user switches between them; this file keeps them. Each is a
// folder under <app data>/bundles named after its work project (its id), so a bundle of a work project the phone already has is an update of it: it replaces the older one, as an upload does on
// the Railway server. A bundle's export time (the manifest's created) tells two versions apart.
//
// WHERE BUNDLES COME FROM
//
//  - Built into the app: the project file zips each folder named in BundleDirs into the app (bundle-<hash>.zip) and lists them in bundles.txt. InstallPackagedAsync() unpacks each on the first
//    run, and again only when an installed build carries a changed zip (its SHA-256 and the id it unpacked to are kept in bundles/.packaged/<zip>.sha256). It never replaces a newer bundle of
//    the same work project: one the user added after installing the app stays.
//  - Removed: the user can remove any bundle but the last (the page keeps one). A removed built-in bundle stays removed, since its zip's stamp is kept; a build with a changed zip of it brings
//    it back, as a new version.
//  - Added or updated on the phone: the page stages the zip the user opens (Stage()), asks before an update replaces a bundle, and then commits it (Commit()) or throws it away (Discard()).
//    The zip may hold the bundle's files at its top level (as upload-bundle zips them) or inside one folder (as Windows' "Send to > Compressed folder" zips the ftt_bundle folder).
//
// TRAPS
//
//  - A zip is unpacked to bundles/.incoming and moved into place only once it has a manifest.json with a work project, so a bad or half-unpacked zip never replaces a working bundle.
//  - Folders starting with "." (.incoming, .packaged) are the store's own and are never listed as bundles. Only one zip is staged at a time; staging another throws the first away.
//  - ZipFile.ExtractToDirectory refuses entries that would land outside the folder, so a zip can't write elsewhere in the app's storage.
//  - created is ISO 8601 (2026-11-07T12:05:31), so comparing it as text orders bundles by export time. A bundle with no created counts as the oldest.
//  - Before several bundles, the app kept its one bundle in <app data>/bundle; RemoveOldBundle() deletes that, since the built-in bundles are unpacked again here.
//
// CODE STRUCTURE
//
// BundleInfo is a bundle's id, folder, names and export time; StagedBundle is a zip unpacked but not yet in place. BundleStore: InstallPackagedAsync() (built-in bundles), Stage(), Commit() and
// Discard() (a zip from the phone), Remove(), Find(), List() and Read() (the bundles there are), and the helpers FindRoot(), SafeId() and RemoveOldBundle().
//

using System.Globalization;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text.Json;

using FTtranslator.Phone.Resources.Strings;

namespace FTtranslator.Phone;

// A bundle: its id (the folder name, from the work project), its folder, its manifest's names, when export-bundle made it, and whether each language is written right to left. The language
// names are empty in a bundle exported before export-bundle wrote them (bundle.py 3.17.2), and both directions are left to right in one exported before it wrote those (bundle.py 3.17.3).
public sealed record BundleInfo(string Id, string Dir, string WorkProject, string SourceProject, string TargetProject, string SourceLanguage, string TargetLanguage, string Created, bool SourceRightToLeft, bool TargetRightToLeft)
{
	// 'French → Spanish', or the project names when the bundle has no language names
	public string LanguagePair => SourceLanguage.Length > 0 && TargetLanguage.Length > 0 ? $"{SourceLanguage} → {TargetLanguage}" : $"{SourceProject} → {TargetProject}";

	// When it was exported, in the phone's date format and UI language ("exported 11/7/26 3:05 PM"), or "export date unknown": a whole phrase, so a sentence can put it in parentheses or after
	// a colon in any language, which "exported {date}" with an "an unknown date" fill-in couldn't do
	public string ExportedText => DateTime.TryParse(Created, CultureInfo.InvariantCulture, DateTimeStyles.None, out DateTime created) ? string.Format(AppResources.Exported, created.ToString("g", CultureInfo.CurrentCulture)) : AppResources.ExportedUnknown;

	// Whether this bundle was exported after another. See TRAPS above.
	public bool IsNewerThan(BundleInfo other)
	{
		return string.CompareOrdinal(Created, other.Created) > 0;
	}
}

// A zip unpacked into bundles/.incoming, waiting for Commit() or Discard(). Info's Dir is the unpacked folder; Id is the id it will have.
public sealed record StagedBundle(string Root, BundleInfo Info);

public static class BundleStore
{
	// The list of built-in bundle zips, written by the project file
	const string PackagedIndex = "bundles.txt";

	static string BundlesDir => Path.Combine(FileSystem.AppDataDirectory, "bundles");
	static string StampsDir => Path.Combine(BundlesDir, ".packaged");
	static string IncomingDir => Path.Combine(BundlesDir, ".incoming");

	// Unpack the built-in bundles that aren't unpacked yet or have changed, unless the phone has a newer bundle of the same work project. See WHERE BUNDLES COME FROM above.
	public static async Task InstallPackagedAsync()
	{
		Directory.CreateDirectory(StampsDir);
		RemoveOldBundle();
		string index;

		using (Stream stream = await FileSystem.OpenAppPackageFileAsync(PackagedIndex))
		using (var reader = new StreamReader(stream))
		{
			index = await reader.ReadToEndAsync();
		}

		foreach (string zipName in index.Split('\n', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries))
		{
			string stampFile = Path.Combine(StampsDir, zipName + ".sha256");
			string hash;

			using (Stream stream = await FileSystem.OpenAppPackageFileAsync(zipName))
			{
				hash = Convert.ToHexString(await SHA256.HashDataAsync(stream));
			}

			// The stamp is the hash, then the id the zip unpacked to. The same zip isn't unpacked again even when its folder has gone: the user removed that bundle. See TRAPS above.
			string[] stamp = File.Exists(stampFile) ? File.ReadAllLines(stampFile) : Array.Empty<string>();

			if (stamp.Length == 2 && stamp[0] == hash)
			{
				continue;
			}

			StagedBundle staged;

			using (Stream stream = await FileSystem.OpenAppPackageFileAsync(zipName))
			{
				staged = Stage(stream);
			}

			BundleInfo? existing = Find(staged.Info.Id);

			if (existing != null && existing.IsNewerThan(staged.Info))
			{
				Discard();
			}
			else
			{
				Commit(staged);
			}

			File.WriteAllLines(stampFile, new[] { hash, staged.Info.Id });
		}
	}

	// Unpack a bundle zip into bundles/.incoming and check it is a bundle. Throws InvalidOperationException, saying why, for a zip that isn't one.
	public static StagedBundle Stage(Stream zip)
	{
		Discard();

		try
		{
			ZipFile.ExtractToDirectory(zip, IncomingDir);
		}
		catch (InvalidDataException)
		{
			Discard();

			throw new InvalidOperationException(AppResources.NotAZip);
		}

		string? root = FindRoot(IncomingDir);
		BundleInfo? info = root == null ? null : Read(root);

		if (root == null || info == null || info.WorkProject.Length == 0)
		{
			Discard();

			throw new InvalidOperationException(AppResources.NotABundle);
		}

		return new StagedBundle(root, info with { Id = SafeId(info.WorkProject) });
	}

	// Put a staged bundle in place, replacing any bundle of its id, and return it as it now is
	public static BundleInfo Commit(StagedBundle staged)
	{
		string bundleDir = Path.Combine(BundlesDir, staged.Info.Id);

		if (Directory.Exists(bundleDir))
		{
			Directory.Delete(bundleDir, true);
		}

		Directory.Move(staged.Root, bundleDir);

		// The bundle was inside a folder of the zip: what's left of the unpacking goes
		Discard();

		return Read(bundleDir)!;
	}

	// Throw away whatever is staged
	public static void Discard()
	{

		if (Directory.Exists(IncomingDir))
		{
			Directory.Delete(IncomingDir, true);
		}
	}

	// Delete a bundle from the phone. The page keeps one bundle at least and switches away from this one first.
	public static void Remove(BundleInfo bundle)
	{

		if (Directory.Exists(bundle.Dir))
		{
			Directory.Delete(bundle.Dir, true);
		}
	}

	// The bundle of an id, or null when the phone hasn't one
	public static BundleInfo? Find(string id)
	{
		string dir = Path.Combine(BundlesDir, id);

		return Directory.Exists(dir) ? Read(dir) : null;
	}

	// The bundles on the phone, by language pair
	public static List<BundleInfo> List()
	{

		if (!Directory.Exists(BundlesDir))
		{
			return new List<BundleInfo>();
		}

		return Directory.GetDirectories(BundlesDir).Where(dir => !Path.GetFileName(dir).StartsWith('.')).Select(Read).OfType<BundleInfo>().OrderBy(bundle => bundle.LanguagePair, StringComparer.CurrentCultureIgnoreCase).ToList();
	}

	// A bundle folder's BundleInfo, or null when its manifest.json is missing or can't be read
	static BundleInfo? Read(string dir)
	{
		string manifestFile = Path.Combine(dir, "manifest.json");

		if (!File.Exists(manifestFile))
		{
			return null;
		}

		try
		{
			using JsonDocument manifest = JsonDocument.Parse(File.ReadAllBytes(manifestFile));
			JsonElement root = manifest.RootElement;

			string Text(string name)
			{
				return root.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.String ? value.GetString() ?? "" : "";
			}

			// A missing flag (an older bundle) is left to right
			bool Flag(string name)
			{
				return root.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.True;
			}

			return new BundleInfo(Path.GetFileName(dir), dir, Text("workProject"), Text("sourceProject"), Text("targetProject"), Text("sourceLanguage"), Text("targetLanguage"), Text("created"), Flag("sourceRightToLeft"), Flag("targetRightToLeft"));
		}
		catch (JsonException)
		{
			return null;
		}
	}

	// The unpacked zip's bundle folder: the top level, or the one folder in it, whichever holds manifest.json
	static string? FindRoot(string unpacked)
	{

		if (File.Exists(Path.Combine(unpacked, "manifest.json")))
		{
			return unpacked;
		}

		string[] folders = Directory.GetDirectories(unpacked);

		return folders.Length == 1 && File.Exists(Path.Combine(folders[0], "manifest.json")) ? folders[0] : null;
	}

	// A work project's name as a folder name: characters a file name can't have become _, and it can't start with "." (the store's own folders do)
	static string SafeId(string workProject)
	{
		char[] invalid = Path.GetInvalidFileNameChars();
		string id = new string(workProject.Select(c => invalid.Contains(c) ? '_' : c).ToArray()).Trim();

		return id.TrimStart('.') is { Length: > 0 } trimmed ? trimmed : "bundle";
	}

	// The one-bundle app's folder and stamp. See TRAPS above.
	static void RemoveOldBundle()
	{

		foreach (string dir in new[] { "bundle", "bundle.incoming" })
		{
			string path = Path.Combine(FileSystem.AppDataDirectory, dir);

			if (Directory.Exists(path))
			{
				Directory.Delete(path, true);
			}
		}

		File.Delete(Path.Combine(FileSystem.AppDataDirectory, "bundle.sha256"));
	}
}
