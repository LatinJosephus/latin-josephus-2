# Nine-record source-contents extension

The existing 30 item records, their attributes, order, text and byte serialization remain untouched. Nine new item/fs records from the approved proposal were inserted immediately before the existing closing list tag. Removing precisely the documented inserted byte interval reproduces the previous registry bytes.

Each new record has work=antiquities; language=Greek; witness=niese; status=VERIFIED; its own book number and companion path; selector `tei-div[type="contents"]`. These records register independent source paratext, not chapter or citation identities. No note, availability, path or source declaration of an earlier witness was changed.

- `contents-antiquities-niese-01` → `assets/xml/antiquities/paratext/niese/book-01-contents.xml` (19 entries).
- `contents-antiquities-niese-02` → `assets/xml/antiquities/paratext/niese/book-02-contents.xml` (8 entries).
- `contents-antiquities-niese-03` → `assets/xml/antiquities/paratext/niese/book-03-contents.xml` (10 entries).
- `contents-antiquities-niese-04` → `assets/xml/antiquities/paratext/niese/book-04-contents.xml` (5 entries).
- `contents-antiquities-niese-06` → `assets/xml/antiquities/paratext/niese/book-06-contents.xml` (15 entries).
- `contents-antiquities-niese-07` → `assets/xml/antiquities/paratext/niese/book-07-contents.xml` (12 entries).
- `contents-antiquities-niese-08` → `assets/xml/antiquities/paratext/niese/book-08-contents.xml` (12 entries).
- `contents-antiquities-niese-09` → `assets/xml/antiquities/paratext/niese/book-09-contents.xml` (16 entries).
- `contents-antiquities-niese-10` → `assets/xml/antiquities/paratext/niese/book-10-contents.xml` (12 entries).

Population: 30 → 39 verified source records; Greek Antiquities: 11 → 20 books. Latin and English availability unchanged.

Before: `3d75560ebb1c5aa67647cb735e7d23de05eaa29fbeb6705c47719ca5a6d063f4`.
After: `3baa8ef1b2e9137b9fbabf3de22d42aca8c3818d4b66d6efe3e239bac9b12092`.
Insertion byte offset: 34561; inserted bytes: 12952.

The full reproducible registry diff follows:

```diff
diff --git a/assets/xml/source-contents.xml b/assets/xml/source-contents.xml
index 5039d2c..b37ac6c 100644
--- a/assets/xml/source-contents.xml
+++ b/assets/xml/source-contents.xml
@@ -979,6 +979,303 @@
           </fs>
         </item>
       <item xml:id="contents-antiquities-bamberg78-14"><fs type="source-contents"><f name="work"><string>antiquities</string></f><f name="book"><string>14</string></f><f name="language"><string>Latin</string></f><f name="witness"><string>bamberg78</string></f><f name="status"><string>VERIFIED</string></f><f name="path"><string>assets/xml/antiquities/paratext/bamberg78/book-14-contents.xml</string></f><f name="selectors"><vColl org="list"><string>tei-div[type="contents"]</string></vColl></f><f name="note"><string></string></f><f name="authority"><string>Current source capitula retained; SR-061 editorial segmentation and supplied numerals [V]–[XII] approved by Richard M. Pollard, 2026-10-08. Narrative divisions are independent; historical export 1 discrepancy remains open.</string></f></fs></item>
+        <item xml:id="contents-antiquities-niese-01">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>1</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-01-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-02">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>2</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-02-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-03">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>3</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-03-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-04">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>4</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-04-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-06">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>6</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-06-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-07">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>7</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-07-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-08">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>8</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-08-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-09">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>9</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-09-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
+        <item xml:id="contents-antiquities-niese-10">
+                  <fs type="source-contents">
+                    <f name="work">
+                      <string>antiquities</string>
+                    </f>
+                    <f name="book">
+                      <string>10</string>
+                    </f>
+                    <f name="language">
+                      <string>Greek</string>
+                    </f>
+                    <f name="witness">
+                      <string>niese</string>
+                    </f>
+                    <f name="status">
+                      <string>VERIFIED</string>
+                    </f>
+                    <f name="path">
+                      <string>assets/xml/antiquities/paratext/niese/book-10-contents.xml</string>
+                    </f>
+                    <f name="selectors">
+                      <vColl org="list">
+                        <string>tei-div[type="contents"]</string>
+                      </vColl>
+                    </f>
+                    <f name="note">
+                      <string/>
+                    </f>
+                    <f name="authority">
+                      <string>Niese printed Greek capitula, directly visually checked against volumes I (1887) and II (1885); Greek Capitula Audit 2026-10-08, master and collation. No narrative identity is inferred.</string>
+                    </f>
+                  </fs>
+                </item>
         </list>
     </body>
   </text>

```
