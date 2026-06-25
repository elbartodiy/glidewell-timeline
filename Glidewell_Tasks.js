/* Glidewell Documentary — task board data.
   ТОЛЬКО задачи ПО ФИЛЬМУ (production). НЕ писать сюда задачи про инструмент/таймлайн/сайт.
   ID = строчная t + номер (t1, t2, …), без дефиса и нулей — чтобы коротко ссылаться в разговоре.
   col: 'ideas' | 'progress' | 'done' | 'archive'.
   Двуязычно: title / notes / links — {en, ru}. Доска по умолчанию EN, RU по переключателю.
   media: пути к файлам в tasks_media/ (НЕ base64). date: YYYY-MM-DD. */
window.GW_TASKS = [
  // ——— IN PROGRESS ———
  { id:"t10", col:"progress", date:"2026-06-25",
    title:{en:"Fri Jun 25 — meet someone internal who knows old-school dentists", ru:"Пт 25 июня — встретиться с сотрудником, кто знает олдскул-дантистов"},
    notes:{en:"Sit down with a Glidewell person who'd know which dentists still send physical (old-school) impressions — to find the old-school hero dentist (t2) / analog lab (t8). Bring concrete questions. Can happen as early as this Friday.",
           ru:"Сесть с сотрудником Glidewell, который знает, кто из дантистов ещё шлёт физические (олдскульные) слепки — чтобы найти героя-дантиста олдскула (t2) / аналоговую лабу (t8). Прийти с конкретными вопросами. Можно уже в эту пятницу."},
    links:[{en:"feeds: t2 (hero dentist) · t8 (analog lab)",ru:"кормит: t2 (герой-дантист) · t8 (аналоговая лаба)"}], media:[] },
  { id:"t9", col:"progress",
    title:{en:"Call Abdul (Hero #1)", ru:"Позвонить Абдулу (Герой №1)"},
    notes:{en:"Hero #1 — CONFIRMED (practice owner, mentors interns). Call to confirm participation, align on the arc (dentist line carries the narrative), and lock shooting windows. Tie to Guiding Leaders / Capstone where it fits.\nNEXT: can call him today — get his email, update his contact info, start the conversation; then gear up to go shoot him (especially if his practice has any special activity worth capturing).",
           ru:"Герой №1 — ПОДТВЕРЖДЁН (владелец практики, менторит интернов). Позвонить: подтвердить участие, сверить арку (линия дантиста несёт нарратив), забить окна съёмок. Привязать к Guiding Leaders / Capstone, где уместно.\nДАЛЬШЕ: можно звонить уже сегодня — взять email, обновить контакт, начать общение; затем готовиться ехать к нему на съёмку (особенно если в практике есть особая активность, которую стоит снять)."},
    links:[{en:"Hero: Dr. Abdul Alas",ru:"Герой: Dr. Abdul Alas"}], media:[] },
  { id:"t1", col:"done",
    title:{en:"Contact Bobbie Norton (Guiding Leaders)", ru:"Связаться с Bobbie Norton (Guiding Leaders)"},
    notes:{en:"DONE — met. Summary + 4 hero-candidate GL alumni (Ellen Paulisick, Nadia Rodriguez, Bianca Clark, Jim Lam) saved on her speaker card. July session 16–17 (film Fri 17); finale/graduation in October (Dentistry on the Rise).",
           ru:"СДЕЛАНО — встретились. Саммари + 4 кандидата-героя из выпускников GL (Ellen Paulisick, Nadia Rodriguez, Bianca Clark, Jim Lam) сохранены на её карточке спикера. Июльская сессия 16–17 (снимаем пт 17); финал/выпуск — октябрь (Dentistry on the Rise)."},
    links:[], media:[] },
  { id:"t7", col:"progress",
    title:{en:"Contact & record Dr. Mike DiTolla (BruxZir origin — top get)", ru:"Связаться и записать Dr. Mike DiTolla (истоки BruxZir — гет №1)"},
    notes:{en:"Top interview get for the 'Revolution' beat. Led the BruxZir launch (2006–2009); charismatic, now back practicing at Valley Dental Esthetics, Lodi, CA (in-state, easy). Independent voice → reads as testimony, not marketing. Ask: how BruxZir was conceived & won over skeptics; analog→digital. Narrative nugget: zirconia took off only when dentists asked their labs for it. Could also speak about Jim for the personal film.\nSTATUS / NEXT: asking Eric (in the email) for DiTolla's contact, or for someone who can set up the interview. Track progress here.",
           ru:"Гет №1 на бит «Революция». Вёл запуск BruxZir (2006–2009); харизматичный, снова практикует в Valley Dental Esthetics, Lodi, CA (в штате, легко). Независимый голос → звучит как свидетельство, не реклама. Спросить: как родился BruxZir и переубедил скептиков; аналог→цифра. Нюанс: цирконий пошёл, когда дантисты сами стали просить его у лабораторий. Может рассказать и про Джима для персонального фильма.\nСТАТУС / ДАЛЬШЕ: спрашиваю у Эрика (в письме) контакт DiTolla или человека, кто организует интервью. Прогресс веду здесь."},
    links:[{en:"Speaker: Mike DiTolla · scenes 3 / 8 / 10",ru:"Спикер: Mike DiTolla · сцены 3 / 8 / 10"}], media:[] },
  { id:"t8", col:"progress",
    title:{en:"Find an old-school dental LAB / technician (still by hand)", ru:"Найти олдскульную дентал-ЛАБОРАТОРИЮ / техника (всё ещё вручную)"},
    notes:{en:"STATUS: stalled — needs Eric's help to move.\nWHAT WE NEED: a present-day technician / lab that still makes crowns by hand — porcelain-fused-to-metal, cast-gold work, removable dentures, repairs; decades in business, owner-run, little or no digital equipment. Real and current, not staged. (This is the LAB/technician side; the old-school hero DENTIST is t2.)\nTWO QUESTIONS FOR ERIC (going into the email): (1) Who inside Glidewell can point us to dentists who still send physical impressions, and to the analog 'holdout' labs? Even one name to call. (2) Do we have a relationship with the Orange Coast College dental-tech program (where Jim studied) — both a source of veteran technicians and a possible story thread back to Jim's origin.\nIN PARALLEL I'll explore: Orange Coast College directly; the NADL / certified-master-ceramist registry; nearby hybrid labs (Keating, Artidental) as starter calls.\nNEXT STEP: meet someone internally on Friday (Jun 25) who may know such dentists.",
           ru:"СТАТУС: подзавис — нужна помощь Эрика, чтобы сдвинуть.\nЧТО НУЖНО: техник / лаборатория, которые и сегодня делают коронки руками — металлокерамика (PFM), цельнолитьё в золоте, съёмные протезы, ремонты; десятилетия на рынке, владелец-оператор, почти без цифрового оборудования. Реально и сейчас, не постановка. (Это сторона ЛАБОРАТОРИИ/техника; олдскульный герой-ДАНТИСТ — это t2.)\nДВА ВОПРОСА ЭРИКУ (идут в письмо): (1) Кто внутри Glidewell может подсказать дантистов, что ещё шлют физические слепки, и «последние из могикан» — аналоговые лаборатории? Хотя бы одно имя для звонка. (2) Есть ли у нас связь с программой зуботехников Orange Coast College (где учился Джим) — это и источник ветеранов-техников, и возможная сюжетная связка с истоком Джима.\nПАРАЛЛЕЛЬНО проработаю: Orange Coast College напрямую; реестр NADL / сертифицированных мастеров-керамистов; соседние гибридные лаборатории (Keating, Artidental) для первых звонков.\nСЛЕДУЮЩИЙ ШАГ: в пятницу (25 июня) встретиться с кем-то внутри, кто может знать таких дантистов."},
    links:[], media:[] },
  { id:"t5", col:"progress",
    title:{en:"Summarize recent meetings (ongoing reminder)", ru:"Саммари последних митингов (постоянное напоминание)"},
    notes:{en:"Standing, permanent reminder — not a one-off. After each meeting, capture a summary; it often needs to live in the recorder/board and isn't always carried into chat. Keep it here as the always-on prompt to write up meetings and fold them into the plan.",
           ru:"Постоянное напоминание — не разовая задача. После каждой встречи делать саммари; оно часто должно жить в рекордере/доске и не всегда переносится в чат. Держим здесь как всегда-висящий пункт: записывать встречи и вплетать в план."},
    links:[], media:[] },

  // ——— IDEAS ———
  { id:"t11", col:"ideas",
    title:{en:"Place Glidewell HT (implants) in the film narrative", ru:"Куда встроить Glidewell HT (импланты) в нарратив фильма"},
    notes:{en:"The Glidewell HT / implant line — and its philosophy — currently isn't really represented in the film's story; it slipped out. Figure out where it belongs across the 14 parts and how to carry it. It has a rich timeline card (2015, Hahn Tapered → Glidewell HT): the 'BruxZir move' applied to the most expensive tooth — premium quality at a fraction of the price, finished with a BruxZir crown, one warranty from implant to restoration; strong fit for the access thesis. Likely homes: Part 10 (philosophy / implants as standard of care) and/or Part 13 (next generation). Implant voices on the roster: Resnik, Kosinski, Patel, Manalili. Decide and work it in.\nTO RESEARCH (Eldar): how implants actually LOOKED and were MADE historically — ~50 years ago vs ~30 years ago vs today, and what changed. We have a feel for crowns/teeth over time, but not for implants. Find references/images/video for the visual 'before vs now' contrast (same trick as the crown). Need to look this up.",
           ru:"Линия Glidewell HT / импланты — и её философия — сейчас почти не представлены в истории фильма; выпали. Продумать, где её место в 14 частях и как её провести. На таймлайне есть подробная карточка (2015, Hahn Tapered → Glidewell HT): «ход BruxZir», применённый к самому дорогому зубу — премиум-качество за долю цены, сверху коронка BruxZir, одна гарантия от импланта до реставрации; сильно ложится на тезис доступности. Вероятные места: Часть 10 (философия / импланты как стандарт) и/или Часть 13 (следующее поколение). Имплант-голоса в ростере: Resnik, Kosinski, Patel, Manalili. Решить и вписать.\nИЗУЧИТЬ (Эльдар): как импланты реально ВЫГЛЯДЕЛИ и как их ДЕЛАЛИ раньше — ~50 лет назад vs ~30 лет назад vs сегодня, и в чём разница. По коронкам/зубам во времени представление есть, по имплантам — нет. Найти референсы/фото/видео для визуального контраста «до vs сейчас» (тот же приём, что с коронкой). Надо поискать инфу."},
    links:[{en:"Milestone: Glidewell HT (2015) · parts 10 / 13",ru:"Веха: Glidewell HT (2015) · части 10 / 13"}], media:[] },
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
    links:[], media:[] },
  { id:"t12", col:"ideas",
    title:{en:"Dig up old Glidewell promo materials (older = better)", ru:"Найти старые промо-материалы Glidewell (чем старше, тем лучше)"},
    notes:{en:"Vintage promos, ads and mailers are great archival texture — for BOTH films (company + Jim). The older and more dated-looking, the better. WHERE TO LOOK (starting points):\n• Glidewell's own marketing / brand archive — ask the marketing team (and our internal contacts) for the historical promo library; this is the likeliest mother lode.\n• Chairside & Lab Perspectives magazines — back issues carry old ads and product promos (newsletter from 1998, full magazine from 2006).\n• The first direct-mail campaigns (1976 onward) — physical flyers/mailers; long-tenured staff (e.g. Phil Venard) or Jim himself may have kept originals.\n• Old print ads in dental trade press (Dental Economics, Dental Products Report, Dentistry Today, etc.), 1980s–2000s.\n• Wayback Machine (archive.org) for old glidewell.com (2001+) — banners, promo pages, launch announcements.\n• YouTube / broadcast — old Glidewell TV/online spots; the Chairside Live archive.\n• Jim's personal archive / Mesa Manor; plus the 'Constant Change' book photos we already extracted.\nGOAL: collect the oldest, most characterful promo material for the analog 'before' texture and the personal film.",
           ru:"Старые промо, реклама и почтовые рассылки — отличная архивная фактура для ОБОИХ фильмов (о компании + о Джиме). Чем старше и «винтажнее» на вид, тем лучше. ГДЕ ИСКАТЬ (отправные точки):\n• Собственный маркетинг / бренд-архив Glidewell — спросить у маркетинга (и наших внутренних контактов) историческую библиотеку промо; самая вероятная золотая жила.\n• Журналы Chairside и Lab Perspectives — в старых выпусках есть реклама и промо продуктов (бюллетень с 1998, полноценный журнал с 2006).\n• Первые кампании прямой почтовой рассылки (с 1976) — физические листовки/мейлеры; у давних сотрудников (напр. Фил Венард) или у самого Джима могут лежать оригиналы.\n• Старая печатная реклама в стоматологической прессе (Dental Economics, Dental Products Report, Dentistry Today и т.п.), 1980-е–2000-е.\n• Wayback Machine (archive.org) для старого glidewell.com (2001+) — баннеры, промо-страницы, анонсы запусков.\n• YouTube / ТВ — старые ролики Glidewell; архив Chairside Live.\n• Личный архив Джима / Mesa Manor; плюс уже извлечённые фото из книги «Constant Change».\nЦЕЛЬ: собрать самый старый и характерный промо-материал для аналоговой фактуры «до» и для личного фильма."},
    links:[], media:[] }

  // ——— DONE / ARCHIVE ——— (пока пусто; сюда — завершённые/отменённые задачи ПО ФИЛЬМУ)
];
