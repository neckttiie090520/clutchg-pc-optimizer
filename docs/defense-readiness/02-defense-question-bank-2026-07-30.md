# ClutchG Thesis Defense Question Bank

**Baseline:** 2026-07-30  
**Use:** ซ้อมตอบจากหลักฐานจริง ไม่ใช่บทพูดท่องจำ

รูปแบบคำตอบที่แนะนำ: **ข้อสรุป → หลักฐาน → ขอบเขต/ข้อจำกัด → งานถัดไป** ถ้าไม่มีหลักฐานให้ตอบว่า “ยังไม่ยืนยัน” แทนการคาดเดา

## A. Problem, scope and contribution

### 1. งานนี้แก้ปัญหาอะไร?
ClutchG ลดความเสี่ยงจากการปรับแต่ง Windows แบบกระจัดกระจายและตรวจสอบย้อนกลับไม่ได้ โดยรวม tweak contracts, risk classification, backup-before-mutation, rollback และ GUI orchestration ไว้ใน workflow เดียว Contribution ไม่ใช่การคิด registry tweak ใหม่ทั้งหมด แต่เป็นการคัดกรอง จัดระบบ และควบคุมการนำไปใช้ให้ตรวจสอบได้

### 2. ขอบเขตที่ไม่ทำคืออะไร?
ไม่รับประกันผลบน hardware/Windows ทุกแบบ ไม่อ้าง performance gain ทั่วไปโดยไม่มี benchmark และไม่ถือว่า static/unit tests แทน privileged runtime validation ปัจจุบัน signed release และ current-source Sandbox revalidation ยังเป็น external gates

### 3. ทำไมต้องศึกษา open-source projects หลายโครงการ?
ใช้เพื่อสร้าง candidate pool และเปรียบเทียบ pattern แต่จำนวน corpus ต้องนิยามให้คงที่ เช่น primary repositories แยกจาก supporting materials การมีหลายแหล่งไม่ทำให้ tweak ถูกต้องอัตโนมัติ จึงต้องผ่าน safety policy, contract review และ V&V อีกชั้น

### 4. Novelty อยู่ตรงไหนถ้า tweak มีอยู่แล้ว?
Novelty เชิงวิศวกรรมอยู่ที่ evidence-based selection, layered execution contract, transaction/rollback controls, risk communication และ traceability ระหว่าง requirement–design–code–test ไม่ควรกล่าวว่า algorithm ทุกตัวเป็นงานค้นพบใหม่

## B. Software engineering process

### 5. ใช้ SDLC แบบใด?
ใช้ modified Waterfall สำหรับ work products และ ISO 29110 gates แต่ implementation เป็น incremental/iterative: batch modules เพิ่มทีละส่วนและ GUI ปรับหลายรอบ เหตุผลคือ thesis ต้องการเอกสารตามลำดับ ขณะที่ requirement ด้าน UX และ safety ต้องเรียนรู้จากการทดสอบ

### 6. ISO/IEC 29110 ช่วยอะไร?
ช่วยกำหนด work products และ control points สำหรับ project management และ software implementation เช่น Project Plan, SRS, SDD, Test Plan/Record, Traceability, Change Request และ Configuration Management คุณค่าคือทำให้การเปลี่ยนแปลงและหลักฐานตรวจย้อนหลังได้ ไม่ใช่เพียงมีไฟล์เอกสารครบ

### 7. Verification กับ Validation ต่างกันอย่างไรในงานนี้?
Verification คือ review/static contracts/unit/integration ว่า “สร้างถูกตามแบบหรือไม่” ส่วน Validation คือ Sandbox/Hyper-V/UAT/benchmark ว่า “ระบบตอบโจทย์ใน environment จริงหรือไม่” ปัจจุบัน automated verification ผ่าน แต่ current-source privileged validation ยังต้องทำ

### 8. ทำไมเอกสาร audit เก่าไม่ถูกลบ?
เอกสารเดือนพฤษภาคมเป็น evidence ของ corrective maintenance: แสดง defect baseline, remediation และ re-verification การแก้ทับจะทำลาย audit trail จึงสร้าง current-state pack ใหม่และระบุว่าเอกสารเก่าเป็น historical

## C. Architecture and design

### 9. Architecture เป็นแบบใด?
เป็น layered desktop architecture: entry/app controller → GUI views/components → core services → external Windows batch engine/data Layering ลด coupling; GUI เรียก core แต่ core ไม่ควรพึ่ง widget implementation

### 10. ทำไมไม่ใช้ microservices?
ระบบเป็น local Windows desktop tool ไม่มี distributed scaling requirement การใช้ microservices เพิ่ม deployment, security และ operational complexity โดยไม่ให้ประโยชน์ตาม scope จึงเป็น overengineering

### 11. GUI เชื่อมกับ batch scripts อย่างไร?
GUI ส่ง intent ไป `ProfileManager`; action catalog แปลงเป็น audited script/argument contracts; `BatchExecutor` validate และเปิด process; output/result ถูกส่งกลับ GUI การสำเร็จต้องอิง return contract ไม่ใช่แค่ process เริ่มได้

### 12. Low coupling / high cohesion แสดงที่ไหน?
Core modules แยกหน้าที่ เช่น backup, execution, profile, updater; views รับผิดชอบ interaction/rendering การแก้ registry allowlist อยู่ใน `BackupManager` และ GUI ตรวจเฉพาะ `backup.success` แทนการฝัง restore logic ใน view

## D. Safety and correctness

### 13. ถ้า backup ล้มเหลวเกิดอะไรขึ้น?
Mutation workflow ถูกออกแบบให้ fail closed และ static/regression contracts ยืนยัน backup-before-mutation ส่วน Python backup UI จะแสดงสำเร็จเฉพาะเมื่อ recovery artifacts สำเร็จ อย่างไรก็ตาม privileged apply/rollback behavior ของ source ปัจจุบันยังต้องยืนยันใน Sandbox

### 14. ป้องกัน restore ไฟล์แปลกปลอมอย่างไร?
Python restore ใช้ six-file `REGISTRY_BACKUPS` allowlist เดียวกับ export, preflight ว่าไฟล์ครบก่อน import และคืนสำเร็จเมื่อครบ 6/6 เท่านั้น Regression tests พิสูจน์ว่า `injected.reg` ไม่ถูก import และ partial failure คืน `False`

### 15. Backup ID ชนกันได้หรือไม่?
เดิมมีความเสี่ยงเมื่อสร้างในวินาทีเดียวกัน ปัจจุบัน `_allocate_backup_path()` สร้าง directory แบบ atomic และใช้ suffix เมื่อชน Regression test freeze เวลาเดียวกันและยืนยัน ID/directory แยกกัน

### 16. ยืนยันว่า rollback คืนค่าทุกอย่างได้หรือไม่?
ยังไม่ควรตอบว่า “ทุกอย่าง” Static contracts และ historical Hyper-V record สนับสนุนหลายกรณี แต่ source หลัง remediation ต้อง fresh apply→verify→rollback ใน disposable environment จึงจะปิด claim นี้ได้

### 17. ป้องกันการปิด Defender/UAC/Windows Update อย่างไร?
มี safety policy, action allowlists และ static tests แต่คำตอบระดับ runtime ต้องอ้าง fresh Sandbox result ที่ query state ก่อน/หลัง หากยังไม่มี ให้ตอบว่าหลักฐานปัจจุบันเป็น source-level control และ historical VM evidence

### 18. Cancellation ปลอดภัยอย่างไร?
มี shared mutation admission, cancellation event ก่อน backup/ระหว่าง action และ process-tree termination ใน `BatchExecutor`; tests ครอบคลุม spawn race และ lifecycle แต่ต้องมี Sandbox scenario ยืนยันว่าไม่มี action ถัดไปเริ่มหลัง cancel

## E. Testing and evidence

### 19. ผลทดสอบล่าสุดคืออะไร?
วันที่ 2026-07-30 รัน release-equivalent suite จาก `clutchg`: 765 collected, 762 passed, 3 skipped, 0 failed in 80.91s; total Python coverage 39%; targeted regressions รอบ Bug Hunter 77/77

### 20. ทำไมมี tests มากกว่า 700 ทั้งที่ทำคนเดียว?
จำนวนนี้รวม parameterized/static contract/regression tests และการพัฒนาเป็นเวลาหลายรอบ ไม่ควรอ้างว่าเขียนด้วยมือทุกบรรทัดในครั้งเดียว กระบวนการใช้ automation และ AI assistance ช่วยเสนอ/สร้าง test candidates แต่ผู้วิจัยกำหนด acceptance criteria ตรวจ source/review failures และรับผิดชอบ final evidence Tests ที่นับต้องรันซ้ำได้และผูกกับ requirement/defect ไม่ใช่นับจำนวนเพื่อความสวยงาม

### 21. Coverage 39% ต่ำกว่า requirement 70% หรือไม่?
ใช่ ถ้า NFR หมายถึง total source coverage ปัจจุบันยังไม่ผ่าน ห้ามเปลี่ยนความหมายย้อนหลังโดยไม่มี change request ทางเลือกที่ถูกต้องคือเพิ่ม meaningful tests หรือแก้ requirement ผ่าน change control พร้อมเหตุผลและกำหนด scope metric ใหม่ โมดูลที่แก้มี 80%/87% แต่ไม่ใช้กลบ total 39%

### 22. ทำไม tests ผ่านแต่ยังไม่ release-ready?
Unit/integration ส่วนมากใช้ mock และไม่พิสูจน์ registry/service/BCD mutation, hardware behavior, certificate หรือ installer upgrade จริง จึงแยก `AUTOMATED_VERIFIED` จาก `EXTERNAL_VERIFICATION_REQUIRED`

### 23. สาม skipped tests คืออะไร?
ก่อนสอบต้องดึงชื่อและเหตุผลจาก raw pytest output/marker report แล้วจัด disposition รายตัว ห้ามตอบเพียงว่า “ไม่สำคัญ” หาก skip แตะ safety requirement ต้องปิดก่อน release

### 24. จะพิสูจน์ test traceability อย่างไร?
ใช้ matrix FR → design component → source → exact test node ID → latest result สำหรับรายการที่ไม่มี test ให้ระบุ manual/VM test หรือ gap ไม่ใช้จำนวนรวมแทน traceability

### 25. Bug Hunter ครอบคลุมทั้ง repository หรือไม่?
ไม่ Triage พบ 26,392 scannable files โดย 26,279 เป็น reference/vendor snapshots ใน `research/` Deep scan รอบนี้เน้น product-owned trust boundaries และระบุ partial coverage ใน artifact อย่างชัดเจน

## F. CI/CD and release

### 26. CI/CD pipeline ทำอะไร?
Contract tests ตรวจ exact version/tag/asset, signing prerequisites, expected publisher และ exact release path Release จริงต้องมี certificate secrets, controlled tag, valid Authenticode, hashes และ retained CI URL

### 27. GitHub governance ถูกเผยแพร่แล้วแค่ไหน?
เผยแพร่ milestone `Defense Readiness 2026`, Issues #5–#11 และ PR #12 แล้ว โดย PR จำกัดขอบเขตไว้ที่ governance templates, runbook และ Project automation ที่ทดสอบแบบ offline ส่วน product release ยังไม่ถูกเผยแพร่ และ GitHub Project ยังรอการอนุมัติ OAuth `project` scope จากผู้วิจัย Working tree ที่ยังไม่ freeze จึงไม่ถูกเหมารวมเข้า commit หรือใช้เป็น official evidence baseline

### 28. Updater ปลอดภัยอย่างไร?
เลือก exact installer identity, stage ใน restricted directory, verify Authenticode/publisher/version และ recheck fingerprint ก่อน launch Fingerprint ป้องกัน local replacement แต่ไม่ใช่ independent provenance; provenance มาจาก signed controlled release

## G. Research validity and performance

### 29. อ้าง performance improvement ได้แค่ไหน?
อ้างได้เฉพาะ workload/hardware/repetition ที่มี raw benchmark หากยังไม่มี current controlled experiment ให้กล่าวเป็น expected effect หรือ design goal ไม่ใช้ช่วง 5–25% เป็น universal result

### 30. Threats to validity มีอะไร?
Hardware heterogeneity, Windows build/driver differences, VM–bare-metal gap, selection bias ของ open-source corpus, mock-heavy automated tests, instrumentation noise และ source drift ระหว่าง test record กับ current checkout วิธีลดคือ freeze hash, repeated measures, environment record, raw data และ separate claims

### 31. Historical Hyper-V 20/20 ใช้ได้หรือไม่?
ใช้เป็น historical V&V ของ baseline วันที่ 2026-04-12 และ evidence ว่าวิธีทดลองเคยทำได้ แต่ไม่รับรอง source หลัง remediation ต้อง rerun current source หรืออธิบาย source/version mapping อย่างตรวจสอบได้

## H. Experimental design, statistics and ethics

### 32. เก็บข้อมูลผู้เข้าร่วมเสร็จแล้วหรือยัง?
ยังไม่ควรอ้างว่าเสร็จจนกว่า `[TBD]` ใน Chapter 6 จะถูกแทนด้วยข้อมูลจริงที่ trace กลับไป consent, raw logs และ environment metadata ได้ ระหว่างนี้สรุปได้เฉพาะผลพัฒนาและ automated verification

### 33. การกำหนด Machine A = Based และ Machine B = Optimized พิสูจน์ causal effect ได้หรือไม่?
ยังมี machine-treatment confounding เพราะความต่างของ firmware, silicon, cooling, storage หรือ background state อาจปะปนกับ treatment ต้องสลับ treatment ข้ามเครื่อง/ใช้ crossover ที่ควบคุมได้ หรือจำกัด claim และระบุ limitation โดยอาจารย์เห็นชอบ

### 34. Counterbalancing ผู้เข้าร่วมแก้ confounding นี้หรือไม่?
Counterbalancing ลำดับ A/B ลด order effect แต่ไม่แยก treatment ออกจาก machine identity หาก treatment ถูกผูกกับเครื่องเดิมตลอด นอกจากนี้ลำดับ Easy→Medium→Hard ที่คงที่ยังทำให้ difficulty ปะปนกับ warm-up/fatigue

### 35. Friedman test ใช้แทน two-factor repeated-measures ANOVA ได้ทั้งหมดหรือไม่?
ไม่ได้โดยอัตโนมัติ Friedman พื้นฐานไม่ประมาณ Machine × Difficulty interaction แบบเดียวกัน ต้องมี analysis plan ที่ statistician/advisor รับรอง รวม assumption checks, interaction-capable fallback, confidence intervals, effect size และ multiplicity handling

### 36. ทำไมต้องมี ethics determination หากความเสี่ยงต่ำ?
มีการรับสมัครผู้เข้าร่วม เก็บข้อมูล ให้ค่าชดเชย และมีประเด็นสุขภาพ/consent จึงต้องมีหลักฐานจากหน่วยงานหรืออาจารย์ที่มีอำนาจว่าเข้าข่าย review, exemption หรือ non-review ไม่ใช้การประเมินของผู้วิจัยเองแทน institutional determination

### 37. ชื่อเรื่องใช้คำว่า “ทักษะผู้เล่น” ได้หรือไม่?
ได้เฉพาะเมื่อมี outcome ที่วัด skill โดยตรง เช่น accuracy, reaction time หรือ task score หากวัด frametime, DPC/ISR, resource use และ satisfaction ควรใช้ “ประสิทธิภาพเกม/ระบบ” หรือเพิ่มและ validate skill measure

## I. AI-assisted development and ethics

### 38. ใช้ AI ในงานหรือไม่?
ใช้เป็นเครื่องมือช่วย search, review, test candidate generation และ document consistency checking ผู้วิจัยยังเป็นผู้กำหนด requirement, ตัดสิน safety policy, ตรวจ diff, รัน/อนุมัติ privileged tests และรับรองผล การใช้จะเปิดเผยตามนโยบายมหาวิทยาลัยและเก็บ traceable artifacts

### 39. ป้องกัน AI สร้างข้อมูลเท็จอย่างไร?
ไม่รับข้อความจาก AI เป็น evidence โดยตรง ทุก claim ต้องย้อนกลับไป raw output, source, test, experiment หรือ reviewer sign-off รายงานเก่าที่ขัดกับ source ถูกจัดเป็น historical/obsolete ไม่ถูกนำมารวมเป็นผลล่าสุด

### 40. ส่วนใดต้องทำโดยมนุษย์?
Participant study, ethics determination, statistical sign-off, privileged Sandbox/VM execution, hardware benchmark, UAT, certificate provisioning, release approval, interpretation of results, thesis rewriting, citation verification และ advisor sign-off

## J. Closing questions

### 41. จุดแข็งที่สุดคืออะไร?
Traceable safety-oriented engineering: defects ถูกเชื่อมจาก finding → fix → regression → full suite และ external limits ถูกระบุแทนการกล่าวเกินจริง

### 42. จุดอ่อนที่สุดคืออะไร?
Participant evidence/ethics/statistical design ยังไม่ปิด, current total coverage 39%, source baseline ยัง dirty/unfrozen และ current-source privileged/release evidence ยังไม่ครบ ต้องพูดตรง ๆ พร้อม closure plan

### 43. ถ้ามีเวลาเพิ่มจะทำอะไรเป็นลำดับแรก?
(1) ปิด ethics/design/statistical gates (2) freeze baseline/hash (3) เก็บ participant evidence จริง (4) rerun Sandbox/apply/rollback (5) reconcile FR/test/numeric claims และ regenerate final PDF

## Phrases to avoid

- “ระบบปลอดภัย 100%”
- “ผ่านทุก Windows และทุก hardware”
- “tests ผ่านจึงไม่มี bug”
- “coverage 39% เพียงพอแน่นอน”
- “Hyper-V 20/20 พิสูจน์ source ปัจจุบัน”
- “AI ทำวิทยานิพนธ์ให้”

ให้แทนด้วยขอบเขต วันที่ หลักฐาน และข้อจำกัดทุกครั้ง
