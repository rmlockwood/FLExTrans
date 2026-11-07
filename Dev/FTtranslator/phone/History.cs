// History.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. The translation history, kept in a JSON file in the app's storage.
//
// OVERVIEW (AI generated, then edited)
//
// The app keeps every translation, newest first, so earlier ones can be read again and copied after the app has closed. Each is a HistoryEntry: the bundle it was made with (the page shows
// only the chosen bundle's), what the screen shows (the source and the translation, or the error) and what trace mode shows (the run record, and the Apertium streams of translations made in
// trace mode). The whole list, every bundle's, is one file, history.json in the app's storage, read when the app starts and written after each change, off the UI thread; it holds the last
// MaxEntries translations.
//
// TRAPS
//
//  - The file is written to history.json.tmp and then moved over history.json, so a write cut short (the app killed mid-write) leaves the old history rather than half a file.
//  - A history file that can't be read (from a later version of the app, say) is set aside as history.json.bad and the app starts with no history, rather than not starting.
//  - Save() takes a lock: the page saves in the background, and two saves close together (a translation, then a delete) mustn't write the temporary file at once. The page passes a copy of
//    the list, so the one it goes on changing is never read here.
//  - The JSON is source-generated (HistoryJson), so it works in a trimmed build. The run record keeps its own JSON names (FTOffline's RunResult), the ones the run records on the server use.
//
// CODE STRUCTURE
//
// HistoryEntry, then HistoryJson (the source-generated serializer), then HistoryStore with Load() and Save().
//

using System.Text.Json;
using System.Text.Json.Serialization;

using FTtranslator.Offline;

namespace FTtranslator.Phone;

public sealed class HistoryEntry
{
	public DateTime When { get; set; }

	// The id of the bundle it was made with (its work project; see Bundles.cs)
	public string Bundle { get; set; } = "";
	public string Source { get; set; } = "";

	// Null when the translation failed, and then Error says why; ErrorDetail is the exception, for trace mode
	public string? Translation { get; set; }
	public string? Error { get; set; }
	public string? ErrorDetail { get; set; }

	// For trace mode: the run record (null when a step threw), and the source and target Apertium streams
	public RunResult? Record { get; set; }
	public string? SourceStream { get; set; }
	public string? TargetStream { get; set; }
}

[JsonSourceGenerationOptions(DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
[JsonSerializable(typeof(List<HistoryEntry>))]
internal partial class HistoryJson : JsonSerializerContext
{
}

public sealed class HistoryStore
{
	// The translations kept, all bundles together; older ones are dropped as new ones come
	public const int MaxEntries = 500;

	readonly string path = Path.Combine(FileSystem.AppDataDirectory, "history.json");
	readonly object saveLock = new object();

	// The saved history, newest first; empty when there is none or it can't be read. See TRAPS above.
	public List<HistoryEntry> Load()
	{

		if (!File.Exists(path))
		{
			return new List<HistoryEntry>();
		}

		try
		{
			return JsonSerializer.Deserialize(File.ReadAllBytes(path), HistoryJson.Default.ListHistoryEntry) ?? new List<HistoryEntry>();
		}
		catch (JsonException)
		{
			File.Move(path, path + ".bad", true);

			return new List<HistoryEntry>();
		}
	}

	// Save the history, newest first, keeping the newest MaxEntries. See TRAPS above.
	public void Save(List<HistoryEntry> entries)
	{

		lock (saveLock)
		{
			string tempPath = path + ".tmp";
			File.WriteAllBytes(tempPath, JsonSerializer.SerializeToUtf8Bytes(entries.Take(MaxEntries).ToList(), HistoryJson.Default.ListHistoryEntry));
			File.Move(tempPath, path, true);
		}
	}
}
