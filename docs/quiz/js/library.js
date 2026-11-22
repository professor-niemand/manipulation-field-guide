/**
 * library.js: loads the one library this copy of the quiz uses.
 *
 * SITE COPY ONLY. The stand-alone Sheet2Quiz app lets people import any spreadsheet.
 * This copy is fixed to the Manipulation Field Guide library, which sits next to the site.
 *
 * On every start it reads the spreadsheet and saves it as one library with a fixed id,
 * so an updated spreadsheet replaces the old card list while quiz history is kept.
 * If the spreadsheet cannot be fetched (offline, first visit not finished), the copy
 * saved on the device is used. Exports: LIB_ID, syncLibrary
 */
import { parseFile } from "./parse.js";
import * as db from "./db.js";

export const LIB_ID = "manipulation-field-guide";

export async function syncLibrary() {
  try {
    const url = document.querySelector('meta[name="library-url"]').content;
    const res = await fetch(url);
    if (!res.ok) throw new Error("HTTP " + res.status);
    const file = new File([await res.blob()], "library.xlsx");
    const { headers, rows } = await parseFile(file);
    // Sensible starting columns: question = Example, answer = Technique (by header name).
    const q = headers.indexOf("Example"), a = headers.indexOf("Technique");
    const old = await db.getLibrary(LIB_ID);
    await db.saveLibrary({
      id: LIB_ID, name: "Manipulation techniques", headers, rows,
      defaults: q >= 0 && a >= 0 ? { qCol: q, aCol: a } : undefined,
      createdAt: old?.createdAt ?? Date.now(),
    });
  } catch (e) { /* offline or not loaded yet: fall through to the saved copy */ }
  return db.getLibrary(LIB_ID);
}
