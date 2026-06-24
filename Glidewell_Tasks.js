/* Glidewell Documentary — task board data.
   ТОЛЬКО задачи ПО ФИЛЬМУ (production). НЕ писать сюда задачи про инструмент/таймлайн/сайт.
   ID = строчная t + номер (t1, t2, …), без дефиса и нулей — чтобы коротко ссылаться в разговоре.
   col: 'ideas' | 'progress' | 'done' | 'archive'.
   Двуязычно: title / notes / links — {en, ru}. Доска по умолчанию EN, RU по переключателю.
   media: пути к файлам в tasks_media/ (НЕ base64). date: YYYY-MM-DD. */
window.GW_TASKS = [
  // ——— IN PROGRESS ———
  { id:"t9", col:"progress",
    title:{en:"Call Abdul (Hero #1)", ru:"Позвонить Абдулу (Герой №1)"},
    notes:{en:"Hero #1 — CONFIRMED (practice owner, mentors interns). Call to confirm participation, align on the arc (dentist line carries the narrative), and lock shooting windows. Tie to Guiding Leaders / Capstone where it fits.",
           ru:"Герой №1 — ПОДТВЕРЖДЁН (владелец практики, менторит интернов). Позвонить: подтвердить участие, сверить арку (линия дантиста несёт нарратив), забить окна съёмок. Привязать к Guiding Leaders / Capstone, где уместно."},
    links:[{en:"Hero: Dr. Abdul Alas",ru:"Герой: Dr. Abdul Alas"}], media:[] },
  { id:"t1", col:"progress",
    title:{en:"Contact Bobbie Norton (Guiding Leaders)", ru:"Связаться с Bobbie Norton (Guiding Leaders)"},
    notes:{en:"Brief her on the project. Our film as a Capstone for the cohort. Find shooting windows (~4 in-person visits per course); who from the cohort to take as heroes / touch-points.",
           ru:"Передать контекст проекта. Наш фильм как Capstone для когорты. Узнать окна съёмок (~4 очных визита за курс), кого из врачей берём в герои/касания."},
    links:[], media:[] },
  { id:"t7", col:"progress",
    title:{en:"Contact & record Dr. Mike DiTolla (BruxZir origin — top get)", ru:"Связаться и записать Dr. Mike DiTolla (истоки BruxZir — гет №1)"},
    notes:{en:"Top interview get for the 'Revolution' beat. Led the BruxZir launch (2006–2009); charismatic, now back practicing at Valley Dental Esthetics, Lodi, CA (in-state, easy). Independent voice → reads as testimony, not marketing. Ask: how BruxZir was conceived & won over skeptics; analog→digital. Narrative nugget: zirconia took off only when dentists asked their labs for it.",
           ru:"Гет №1 на бит «Революция». Вёл запуск BruxZir (2006–2009); харизматичный, снова практикует в Valley Dental Esthetics, Lodi, CA (в штате, легко). Независимый голос → звучит как свидетельство, не реклама. Спросить: как родился BruxZir и переубедил скептиков; аналог→цифра. Нюанс: цирконий пошёл, когда дантисты сами стали просить его у лабораторий."},
    links:[{en:"Speaker: Mike DiTolla · scenes 3 / 8 / 10",ru:"Спикер: Mike DiTolla · сцены 3 / 8 / 10"}], media:[] },
  { id:"t8", col:"progress",
    title:{en:"Find an old-school dental LAB / technician (still by hand)", ru:"Найти олдскульную дентал-ЛАБОРАТОРИЮ / техника (всё ещё вручную)"},
    notes:{en:"Distinct from t2 — t2 is the HERO DENTIST; here we need a TECHNICIAN / lab that still makes crowns by hand today (PFM, cast gold, removables, repairs). Real, present-day, NOT a reconstruction.\nChannels (by priority):\n1) Ask Glidewell (Bobbie / sales / Glidewell Direct) — they know which dentists still send physical impressions and which labs are analog holdouts. We need the technician, but Glidewell may know.\n2) Orange Coast College dental-tech program (Costa Mesa — where Jim studied!) — instructors know veteran master ceramists & old labs. Take the department into work.\n3) NADL (nadl.org) + CDT registry (National Board for Certification) — find certified master ceramists locally.\nOld-school signals: PFM / full-cast gold / removables / repairs, 'master ceramist', decades in business, owner-operated, little/no CAD-CAM.\nHybrid starting-call leads (Irvine/OC, do digital + hand): Keating Dental Lab, Artidental Lab, Essential Smiles — but the pure analog artisan is better found via channels 1–2.",
           ru:"Отдельно от t2 — t2 про ГЕРОЯ-ДАНТИСТА; здесь нужен ТЕХНИК / лаборатория, что и сегодня делает коронки вручную (PFM, цельнолитьё-золото, съёмники, ремонты). Реально, сейчас, НЕ реконструкция.\nКаналы (по приоритету):\n1) Спросить у Glidewell (Бобби / отдел продаж / Glidewell Direct) — они знают, кто из дантистов ещё шлёт физ. слепки и какие лабы аналоговые «последние из могикан». Нам нужен техник, но Glidewell может знать.\n2) Orange Coast College — программа зуботехников (Коста-Меса, там учился Джим!) — преподаватели знают ветеранов-керамистов и старые лабы. Кафедру — в проработку.\n3) NADL (nadl.org) + реестр CDT (National Board for Certification) — найти сертифицированных мастеров-керамистов локально.\nСигналы олдскула: PFM / золото / съёмники / ремонты, «master ceramist», десятилетия на рынке, владелец-оператор, почти нет CAD/CAM.\nГибридные зацепки для первых звонков (Irvine/OC, делают и цифру, и руками): Keating Dental Lab, Artidental Lab, Essential Smiles — но чистую аналоговую артель надёжнее искать через каналы 1–2."},
    links:[{en:"NADL: nadl.org · related but different: t2 (hero dentist)",ru:"NADL: nadl.org · связано, но другое: t2 (герой-дантист)"}], media:[] },
  { id:"t5", col:"progress",
    title:{en:"Consolidate everyone's meeting notes → shooting plan", ru:"Свести заметки участников встречи → план съёмок"},
    notes:{en:"Merge what to add / what's not important from all participants, then build the shooting plan.",
           ru:"Свести воедино «что добавить / что неважно» от всех участников, затем строить план съёмок."},
    links:[], media:[] },

  // ——— IDEAS ———
  { id:"t2", col:"ideas",
    title:{en:"Find an old-school dentist (impressions)", ru:"Найти дантиста, работающего «по-старому» (слепки)"},
    notes:{en:"For the \"before\" contrast and the Hero 2 (old-school) arc. Which clients still send the most archaic impressions? Possibly one of the side-heroes.",
           ru:"Для контраста «до» и арки Hero 2 (old-school). Кто из клиентов присылает самые архаичные слепки? Возможно — один из сайд-героев."},
    links:[], media:[] },
  { id:"t3", col:"ideas",
    title:{en:"Get speaker photo/video references from the company", ru:"Получить от компании фото/видео-референсы спикеров"},
    notes:{en:"Glidewell internal library; video clips for almost everyone. For casting and vetting the speakers.",
           ru:"Внутренняя библиотека Glidewell; видеоклипы почти на всех. Для каста и выверки спикеров."},
    links:[], media:[] },
  { id:"t6", col:"ideas",
    title:{en:"Shoot shared footage now (2 films in parallel)", ru:"Снимать общий материал сразу (2 фильма параллельно)"},
    notes:{en:"Two films are planned (company + Jim) — capture shared footage at once while the same people and locations are gathered.",
           ru:"Планируется 2 фильма (о компании + о Джиме) — снимать общий материал сразу, пока собраны те же люди и площадки."},
    links:[], media:[] }

  // ——— DONE / ARCHIVE ——— (пока пусто; сюда — завершённые/отменённые задачи ПО ФИЛЬМУ)
];
