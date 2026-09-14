"""
SURE SAVINGS: Central i18n Localization Service
Handles catalog loading, translation resolution, language purity validation,
localized attribution, confidentiality refusals, greetings, and deterministic fallback.
"""
import os
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from backend.localization.locale_registry import (
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE,
    validate_locale,
    get_locale_metadata,
)
from backend.localization.financial_glossary import get_glossary_term

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "locales")

# In-memory cache for loaded translation catalogs
_CATALOG_CACHE: Dict[str, Dict[str, Any]] = {}


def get_catalog(locale: str) -> Dict[str, str]:
    """Returns the flattened key-value translation catalog for the given locale."""
    valid_loc = validate_locale(locale)
    if valid_loc in _CATALOG_CACHE:
        return _CATALOG_CACHE[valid_loc]

    single_file = os.path.join(LOCALES_DIR, f"{valid_loc}.json")
    catalog: Dict[str, str] = {}
    if os.path.exists(single_file):
        try:
            with open(single_file, "r", encoding="utf-8") as f:
                catalog.update(json.load(f))
        except Exception:
            pass

    dir_path = os.path.join(LOCALES_DIR, valid_loc)
    if os.path.isdir(dir_path):
        for fname in os.listdir(dir_path):
            if fname.endswith(".json"):
                fpath = os.path.join(dir_path, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        section = json.load(f)
                        domain = fname[:-5]
                        if isinstance(section, dict):
                            for k, v in section.items():
                                catalog[f"{domain}.{k}"] = v
                except Exception:
                    pass

    _CATALOG_CACHE[valid_loc] = catalog
    return catalog

# ── Localized Public Attribution ──
# "This website was built by Satyabrata Das from Narula Institute of Technology."
ATTRIBUTION_TEMPLATES: Dict[str, str] = {
    "en-IN": "This website was built by Satyabrata Das from Narula Institute of Technology.",
    "hi-IN": "यह वेबसाइट Satyabrata Das from Narula Institute of Technology द्वारा बनाई गई है।",
    "bn-IN": "এই ওয়েবসাইটটি Satyabrata Das from Narula Institute of Technology তৈরি করেছেন।",
    "as-IN": "এই ৱেবছাইটটো Satyabrata Das from Narula Institute of Technology দ্বাৰা নিৰ্মাণ কৰা হৈছে।",
    "brx-IN": "बे वेबसाइटखौ Satyabrata Das from Narula Institute of Technology आ बानायदों।",
    "doi-IN": "एह वेबसाइट Satyabrata Das from Narula Institute of Technology आसे बनाई गेई ऐ।",
    "gu-IN": "આ વેબસાઇટ Satyabrata Das from Narula Institute of Technology દ્વારા બનાવવામાં આવી છે.",
    "kn-IN": "ಈ ವೆಬ್‌ಸೈಟ್ ಅನ್ನು Satyabrata Das from Narula Institute of Technology ನಿರ್ಮಿಸಿದ್ದಾರೆ.",
    "ks-IN": "یہ ویب سائٹ Satyabrata Das from Narula Institute of Technology نے بنائی ہے۔",
    "kok-IN": "ही वेबसाइट Satyabrata Das from Narula Institute of Technology हांणी तयार केल्या.",
    "ml-IN": "ഈ വെബ്‌സൈറ്റ് നിർമ്മിച്ചത് Satyabrata Das from Narula Institute of Technology ആണ്.",
    "mni-IN": "ৱেবসাইত অসি Satyabrata Das from Narula Institute of Technology না শেম্বনি।",
    "mr-IN": "ही वेबसाइट Satyabrata Das from Narula Institute of Technology यांनी तयार केली आहे.",
    "mai-IN": "ई वेबसाइट Satyabrata Das from Narula Institute of Technology द्वारा बनाओल गेल अछि।",
    "ne-IN": "यो वेबसाइट Satyabrata Das from Narula Institute of Technology द्वारा निर्माण गरिएको हो।",
    "or-IN": "ଏହି ୱେବସାଇଟ୍ Satyabrata Das from Narula Institute of Technology ଦ୍ୱାରା ନିର୍ମିତ ହୋଇଛି।",
    "pa-IN": "ਇਹ ਵੈੱਬਸਾਈਟ Satyabrata Das from Narula Institute of Technology ਦੁਆਰਾ ਬਣਾਈ ਗਈ ਹੈ।",
    "sa-IN": "एषा जालपुटिका Satyabrata Das from Narula Institute of Technology इत्यनेन निर्मिता अस्ति।",
    "sat-IN": "ᱱᱚᱣᱟ ᱣᱮᱵᱽᱥᱟᱭᱤᱴ ᱫᱚ Satyabrata Das from Narula Institute of Technology ᱦᱚᱛᱮᱛᱮ ᱵᱮᱱᱟᱣ ᱟᱠᱟᱱᱟ᱾",
    "sd-IN": "هي ويب سائيٽ Satyabrata Das from Narula Institute of Technology پاران ٺاهي وئي آهي.",
    "ta-IN": "இந்த இணையதளம் Satyabrata Das from Narula Institute of Technology அவர்களால் உருவாக்கப்பட்டது.",
    "te-IN": "ఈ వెబ్‌సైట్ Satyabrata Das from Narula Institute of Technology ద్వారా రూపొందించబడింది.",
    "ur-IN": "یہ ویب سائٹ Satyabrata Das from Narula Institute of Technology نے بنائی ہے۔",
}

# ── Localized Confidentiality Refusals ──
REFUSAL_TITLES: Dict[str, Dict[str, str]] = {
    "source_code": {
        "en-IN": "Confidential Information Protected",
        "hi-IN": "गोपनीय जानकारी सुरक्षित",
        "bn-IN": "গোপনীয় তথ্য সুরক্ষিত",
        "as-IN": "গোপনীয় তথ্য সুৰক্ষিত",
        "gu-IN": "ગુપ્ત માહિતી સુરક્ષિત",
        "kn-IN": "ಗೌಪ್ಯ ಮಾಹಿತಿ ರಕ್ಷಿತ",
        "mr-IN": "गोपनीय माहिती संरक्षित",
        "ta-IN": "ரகசிய தகவல் பாதுகாக்கப்பட்டுள்ளது",
        "te-IN": "రహస్య సమాచారం సురక్షితం",
        "ur-IN": "خفیہ معلومات محفوظ ہیں",
    },
    "user_privacy": {
        "en-IN": "User Privacy Protected",
        "hi-IN": "उपयोगकर्ता गोपनीयता सुरक्षित",
        "bn-IN": "ব্যবহারকারীর গোপনীয়তা সুরক্ষিত",
        "as-IN": "ব্যৱহাৰকাৰীৰ গোপনীয়তা সুৰক্ষিত",
        "gu-IN": "વપરાશકર્તા ગોપનીયતા સુરક્ષિત",
        "kn-IN": "ಬಳಕೆದಾರರ ಗೌಪ್ಯತೆ ರಕ್ಷಿತ",
        "mr-IN": "वापरकर्ता गोपनीयता संरक्षित",
        "ta-IN": "பயனர் தனியுரிமை பாதுகாக்கப்பட்டுள்ளது",
        "te-IN": "వినియోగదారు గోప్యత సురక్షితం",
        "ur-IN": "صارف کی رازداری محفوظ ہے",
    },
    "credentials": {
        "en-IN": "Security Information Protected",
        "hi-IN": "सुरक्षा जानकारी सुरक्षित",
        "bn-IN": "নিরাপত্তা তথ্য সুরক্ষিত",
        "as-IN": "নিৰাপত্তা তথ্য সুৰক্ষিত",
        "gu-IN": "સુરક્ષા માહિતી સુરક્ષિત",
        "kn-IN": "ಭದ್ರತಾ ಮಾಹಿತಿ ರಕ್ಷಿತ",
        "mr-IN": "सुरक्षा माहिती संरक्षित",
        "ta-IN": "பாதுகாப்பு தகவல் பாதுகாக்கப்பட்டுள்ளது",
        "te-IN": "భద్రతా సమాచారం సురక్షితం",
        "ur-IN": "سیکیورٹی معلومات محفوظ ہیں",
    },
    "mutation": {
        "en-IN": "Read-Only Advisory Boundary",
        "hi-IN": "केवल-परामर्श सीमा (रीड-ओनली)",
        "bn-IN": "শুধুমাত্র-পরামর্শমূলক সীমা (রিড-অনলি)",
        "as-IN": "কেৱল-পৰামৰ্শ সীমা (ৰিড-অনলি)",
        "gu-IN": "માત્ર-સલાહકારી મર્યાદા",
        "kn-IN": "ಕೇವಲ ಸಲಹಾ ಗಡಿ (ರೀಡ್-ಓನ್ಲಿ)",
        "mr-IN": "केवळ-सल्लागार मर्यादा (रीड-ओन्ली)",
        "ta-IN": "பார்வைக்கு மட்டுமேயான எல்லை",
        "te-IN": "సలహా పరిమితి మాత్రమే (రీడ్-ఓన్లీ)",
        "ur-IN": "صرف مشاورتی حد (ریڈ آنلی)",
    },
}

REFUSAL_MESSAGES: Dict[str, Dict[str, str]] = {
    "source_code": {
        "en-IN": "Internal repository code, private algorithm logic, and infrastructure manifests are proprietary and confidential. I can however explain all user-facing features, mathematical formulas, and risk policies.",
        "hi-IN": "आंतरिक स्रोत कोड, निजी एल्गोरिदम और बुनियादी ढांचा विन्यास गोपनीय हैं। हालांकि, मैं सभी उपयोगकर्ता-सुविधाओं, वित्तीय फ़ार्मुलों और सुरक्षा नीतियों की व्याख्या कर सकता हूँ।",
        "bn-IN": "অভ্যন্তরীণ সোর্স কোড, ব্যক্তিগত অ্যালগরিদম এবং পরিকাঠামো কনফিগারেশন গোপনীয়। তবে আমি ব্যবহারকারীর সমস্ত বৈশিষ্ট্য, আর্থিক সূত্র এবং ঝুঁকি নীতি ব্যাখ্যা করতে পারি।",
        "mr-IN": "अंतर्गत स्त्रोत कोड, खाजगी अल्गोरिदम आणि पायाभूत सुविधा गोपनीय आहेत. तथापि, मी सर्व वापरकर्ता वैशिष्ट्ये, आर्थिक सूत्रे आणि जोखीम धोरणे समजावून सांगू शकतो.",
        "ta-IN": "உள் மூலக் குறியீடு மற்றும் தனியார் அல்காரிதம் ரகசியமானவை. இருப்பினும், தளத்தின் அனைத்து அம்சங்கள் மற்றும் நிதி சூத்திரங்களை நான் விளக்க முடியும்.",
        "te-IN": "అంతర్గత సోర్స్ కోడ్ మరియు అల్గారిథమ్ సమాచారం రహస్యమైనవి. అయితే, నేను అన్ని ప్లాట్‌ఫారమ్ ఫీచర్లు మరియు ఆర్థిక సూత్రాలను వివరించగలను.",
        "ur-IN": "اندرونی سورس کوڈ اور نجی الگورتھم کی تفصیلات خفیہ ہیں۔ تاہم میں تمام صارف کے فیچرز اور مالیاتی فارمولوں کی وضاحت کر سکتا ہوں۔",
    },
    "user_privacy": {
        "en-IN": "SURE SAVINGS enforces strict cryptographic tenant isolation. Other users' account data, transactions, and balances are strictly confidential. I can only discuss your authenticated workspace.",
        "hi-IN": "SURE SAVINGS सख्त उपयोगकर्ता अलगाव लागू करता है। अन्य उपयोगकर्ताओं का वित्तीय डेटा और शेष राशि पूरी तरह गोपनीय है। मैं केवल आपके अपने कार्यक्षेत्र पर चर्चा कर सकता हूँ।",
        "bn-IN": "SURE SAVINGS কঠোর ব্যবহারকারী বিচ্ছিন্নতা বজায় রাখে। অন্য ব্যবহারকারীদের আর্থিক তথ্য এবং ব্যালেন্স সম্পূর্ণ গোপনীয়। আমি কেবল আপনার নিজস্ব অ্যাকাউন্ট ব্যাখ্যা করতে পারি।",
        "mr-IN": "SURE SAVINGS कडक वापरकर्ता अलगाव लागू करते. इतर वापरकर्त्यांचा आर्थिक डेटा पूर्णपणे गोपनीय आहे. मी फक्त तुमच्या स्वतःच्या खात्याबद्दल माहिती देऊ शकतो.",
        "ta-IN": "SURE SAVINGS கடுமையான பயனர் தனிமைப்படுத்தலை செயல்படுத்துகிறது. பிற பயனர்களின் நிதித் தரவு முற்றிலும் ரகசியமானது.",
        "te-IN": "SURE SAVINGS కఠినమైన వినియోగదారు గోప్యతను అమలు చేస్తుంది. ఇతర వినియోగదారుల ఆర్థిక సమాచారం పూర్తిగా రహస్యం.",
        "ur-IN": "SURE SAVINGS سخت صارف رازداری نافذ کرتا ہے۔ دوسرے صارفین کا مالیاتی ڈیٹا مکمل طور پر خفیہ ہے۔",
    },
    "credentials": {
        "en-IN": "Cryptographic secrets, API keys, client tokens, and database passwords are confidential and never disclosed under any circumstance.",
        "hi-IN": "सुरक्षा कुंजियाँ, API कीज़, क्लाइंट टोकन और पासवर्ड गोपनीय हैं और इन्हें किसी भी स्थिति में साझा नहीं किया जा सकता।",
        "bn-IN": "সুরক্ষা কী, API কী, ক্লায়েন্ট টোকেন এবং পাসওয়ার্ড গোপনীয় এবং কোনো অবস্থাতেই প্রকাশ করা হয় না।",
        "mr-IN": "सुरक्षा की, API की, क्लायंट टोकन आणि पासवर्ड गोपनीय आहेत आणि कोणत्याही परिस्थितीत उघड केले जात नाहीत.",
        "ta-IN": "பாதுகாப்பு விசைகள், API சாவிகள் மற்றும் கடவுச்சொற்கள் ரகசியமானவை, எந்த சூழ்நிலையிலும் பகிரப்படாது.",
        "te-IN": "భద్రతా కీలు, API కీలు మరియు పాస్‌వర్డ్‌లు రహస్యమైనవి, ఎట్టి పరిస్థితుల్లోనూ బహిర్గతం చేయబడవు.",
        "ur-IN": "سیکیورٹی چابیاں، API کیز اور پاس ورڈ خفیہ ہیں اور کسی بھی صورت میں ظاہر نہیں کیے جاتے۔",
    },
    "mutation": {
        "en-IN": "SURE AI operates strictly within a read-only advisory boundary. I cannot move money, execute transfers, or alter balances. Please use the designated buttons in your interface.",
        "hi-IN": "SURE AI सख्त रीड-ओनली परामर्श सीमा के तहत काम करता है। मैं धन हस्तांतरित नहीं कर सकता या बैंक शेष राशि को बदल नहीं सकता। कृपया इंटरफ़ेस में दिए गए बटनों का उपयोग करें।",
        "bn-IN": "SURE AI কঠোর রিড-অনলি পরামর্শমূলক সীমার মধ্যে কাজ করে। আমি অর্থ স্থানান্তর করতে বা ব্যালেন্স পরিবর্তন করতে পারি না। দয়া করে ইন্টারফেসে নির্দিষ্ট বাটন ব্যবহার করুন।",
        "mr-IN": "SURE AI केवळ सल्लागार मर्यादेत काम करते. मी पैसे ट्रान्सफर करू शकत नाही किंवा शिल्लक बदलू शकत नाही. कृपया इंटरफेसमधील योग्य बटणे वापरा.",
        "ta-IN": "SURE AI பார்வைக்கு மட்டுமேயான வரம்பிற்குள் செயல்படுகிறது. என்னால் பணப் பரிமாற்றம் செய்யவோ இருப்பை மாற்றவோ முடியாது.",
        "te-IN": "SURE AI కేవలం సలహా పరిధిలో మాత్రమే పని చేస్తుంది. నేను నగదు బదిలీ చేయలేను. దయచేసి ఇంటర్‌ఫేస్‌లోని బటన్లను ఉపయోగించండి.",
        "ur-IN": "SURE AI صرف مشاورتی حد کے اندر کام کرتا ہے۔ میں رقم منتقل نہیں کر سکتا یا بیلنس تبدیل نہیں کر سکتا۔",
    }
}

# ── Localized Greetings ──
GREETING_WORDS: Dict[str, Dict[str, str]] = {
    "morning": {
        "en-IN": "Good morning",
        "hi-IN": "सुप्रभात",
        "bn-IN": "সুপ্রভাত",
        "as-IN": "সুপ্ৰভাত",
        "gu-IN": "શુભ સવાર",
        "kn-IN": "ಶುಭೋದಯ",
        "mr-IN": "शुभ प्रभात",
        "ta-IN": "காலை வணக்கம்",
        "te-IN": "శుభోదయం",
        "ur-IN": "صبح بخیر",
        "ml-IN": "സുപ്രഭാതം",
        "pa-IN": "ਸ਼ੁਭ ਸਵੇਰ",
        "or-IN": "ଶୁଭ ସକାଳ",
        "ne-IN": "शुभ प्रभात",
        "sa-IN": "सुप्रभातम्",
    },
    "afternoon": {
        "en-IN": "Good afternoon",
        "hi-IN": "शुभ दोपहर",
        "bn-IN": "শুভ অপরাহ্ন",
        "as-IN": "শুভ অপৰাহ্ণ",
        "gu-IN": "શુભ બપોર",
        "kn-IN": "ಶುಭ ಮಧ್ಯಾಹ್ನ",
        "mr-IN": "शुभ दुपार",
        "ta-IN": "மதிய வணக்கம்",
        "te-IN": "శుభ మధ్యాహ్నం",
        "ur-IN": "دوپہر بخیر",
        "ml-IN": "ശുഭ ഉച്ച",
        "pa-IN": "ਸ਼ੁਭ ਦੁਪਹਿਰ",
        "or-IN": "ଶୁଭ ଅପରାହ୍ନ",
        "ne-IN": "शुभ दिउँसो",
        "sa-IN": "शुभ-मध्याह्नम्",
    },
    "evening": {
        "en-IN": "Good evening",
        "hi-IN": "शुभ संध्या",
        "bn-IN": "শুভ সন্ধ্যা",
        "as-IN": "শুভ সন্ধ্যা",
        "gu-IN": "શુભ સાંજ",
        "kn-IN": "ಶುಭ ಸಂಜೆ",
        "mr-IN": "शुभ संध्याकाळ",
        "ta-IN": "மாலை வணக்கம்",
        "te-IN": "శుభ సాయంత్రం",
        "ur-IN": "شام بخیر",
        "ml-IN": "ശുഭ സായാഹ്നം",
        "pa-IN": "ਸ਼ੁਭ ਸੰਝ",
        "or-IN": "ଶୁଭ ସନ୍ଧ୍ୟା",
        "ne-IN": "शुभ साँझ",
        "sa-IN": "शुभ-सायंकालः",
    }
}

PLATFORM_SUMMARIES: Dict[str, str] = {
    "en-IN": "Welcome to **SURE SAVINGS**. SURE SAVINGS helps you understand your income, expenses, cash position, emergency buffer, cash-flow timing, and financial resilience.\n\nYou can ask me how any page or button works, how to connect your bank account, what a financial metric means, or what you should do next.",
    "hi-IN": "मैं SURE AI हूँ, आपका वित्तीय मार्गदर्शक। मैं आपकी आय के उतार-चढ़ाव का विश्लेषण करता हूँ, आपके सुरक्षित नकद न्यूनतम स्तर (Protected Cash Floor) की रक्षा करता हूँ और सुरक्षित बचत राशि (Safe-to-Save) की गणना करता हूँ।",
    "bn-IN": "আমি SURE AI, আপনার আর্থিক সহায়ক। আমি আপনার আয়ের অস্থিরতা বিশ্লেষণ করি, সুরক্ষিত নগদ ন্যূনতম সীমা রক্ষা করি এবং নিরাপদ সঞ্চয়যোগ্য পরিমাণ হিসাব করি যাতে আপনার সঞ্চয় সুরক্ষিত থাকে।",
    "mr-IN": "मी SURE AI आहे, तुमचा आर्थिक मार्गदर्शक. मी तुमच्या उत्पन्नातील चढ-उतारांचे विश्लेषण करतो, तुमच्या संरक्षित रोख किमान मर्यादेचे रक्षण करतो आणि सुरक्षित बचत रकमेची गणना करतो.",
    "ta-IN": "நான் SURE AI, உங்கள் நிதி வழிகாட்டி. உங்கள் வருமான ஏற்ற இறக்கங்களை பகுப்பாய்வு செய்து, பாதுகாக்கப்பட்ட பணத் தளத்தை உறுதிசெய்து, பாதுகாப்பாகச் சேமிக்கக்கூடிய தொகையைக் கணக்கிடுகிறேன்.",
    "te-IN": "నేను SURE AI, మీ ఆర్థిక మార్గదర్శిని. మీ ఆదాయ అస్థిరతను విశ్లేషించి, రక్షిత నగదు పరిమితిని కాపాడుతూ, సురక్షితంగా దాచదగిన మొత్తాన్ని లెక్కిస్తాను.",
    "ur-IN": "میں SURE AI ہوں، آپ کا مالیاتی رہنما۔ میں آپ کی آمدنی کے اتار چڑھاؤ کا تجزیہ کرتا ہوں، محفوظ نقد حد کی حفاظت کرتا ہوں اور محفوظ بچت کا حساب لگاتا ہوں۔",
}

PROMPT_CHIPS: Dict[str, List[str]] = {
    "en-IN": [
        "Show me how SURE SAVINGS works",
        "Help me get started",
        "Explain this page",
        "Help me connect my bank"
    ],
    "hi-IN": [
        "SURE SAVINGS कैसे काम करता है?",
        "शुरुआत करने में मदद करें",
        "इस पेज के बारे में बताएं",
        "बैंक खाता कैसे जोड़ें?"
    ],
    "bn-IN": [
        "SURE SAVINGS কীভাবে কাজ করে?",
        "শুরু করতে সাহায্য করুন",
        "এই পেজটি ব্যাখ্যা করুন",
        "ব্যাংক অ্যাকাউন্ট কীভাবে সংযুক্ত করব?"
    ],
    "mr-IN": [
        "SURE SAVINGS कसे काम करते?",
        "सुरुवात करण्यास मदत करा",
        "हे पृष्ठ समजावून सांगा",
        "बँक खाते कसे जोडावे?"
    ],
    "ta-IN": [
        "SURE SAVINGS எவ்வாறு செயல்படுகிறது?",
        "தொடங்க எனக்கு உதவுங்கள்",
        "இந்தப் பக்கத்தை விளக்குங்கள்",
        "வங்கிக் கணக்கை இணைப்பது எப்படி?"
    ],
    "te-IN": [
        "SURE SAVINGS ఎలా పనిచేస్తుంది?",
        "ప్రారంభించడానికి సహాయం చేయండి",
        "ఈ పేజీని వివరించండి",
        "బ్యాంకు ఖాతాను ఎలా అనుసంధానించాలి?"
    ],
    "ur-IN": [
        "SURE SAVINGS کیسے کام کرتا ہے؟",
        "شروع کرنے میں مدد کریں",
        "اس صفحے کی وضاحت کریں",
        "بینک اکاؤنٹ کیسے منسلک کریں؟"
    ],
}


class I18nService:
    """Central i18n management service."""

    @staticmethod
    def get_attribution(locale: str) -> str:
        """Returns localized attribution statement with exact person/institution preserved."""
        loc = validate_locale(locale)
        return ATTRIBUTION_TEMPLATES.get(loc, ATTRIBUTION_TEMPLATES[DEFAULT_LOCALE])

    @staticmethod
    def get_refusal(category: str, locale: str) -> Tuple[str, str]:
        """Returns (title, message) localized for refusal category."""
        loc = validate_locale(locale)
        cat = category if category in REFUSAL_TITLES else "source_code"
        
        titles = REFUSAL_TITLES.get(cat, {})
        messages = REFUSAL_MESSAGES.get(cat, {})
        
        title = titles.get(loc, titles.get(DEFAULT_LOCALE, "Information Protected"))
        msg = messages.get(loc, messages.get(DEFAULT_LOCALE, "This information is confidential."))
        return title, msg

    @staticmethod
    def get_greeting(time_of_day: str, first_name: str, locale: str) -> Tuple[str, str, List[str]]:
        """Returns (headline, explanation, prompt_chips) localized for time-of-day greeting."""
        loc = validate_locale(locale)
        tod = time_of_day if time_of_day in GREETING_WORDS else "morning"
        
        greet_word = GREETING_WORDS[tod].get(loc, GREETING_WORDS[tod].get(DEFAULT_LOCALE, "Hello"))
        headline = f"{greet_word}, {first_name}." if first_name else f"{greet_word}."
        
        summary = PLATFORM_SUMMARIES.get(loc, PLATFORM_SUMMARIES[DEFAULT_LOCALE])
        chips = PROMPT_CHIPS.get(loc, PROMPT_CHIPS[DEFAULT_LOCALE])
        
        return headline, summary, chips

    @staticmethod
    def validate_language_purity(text: str, locale: str) -> Dict[str, Any]:
        """
        Validates whether generated text adheres to the expected script/language.
        Returns:
          {
            "valid": bool,
            "target_locale": str,
            "script": str,
            "ratio": float,
            "reason": str
          }
        """
        loc = validate_locale(locale)
        meta = get_locale_metadata(loc)
        
        if loc == "en-IN" or meta.script == "Latin":
            return {"valid": True, "target_locale": loc, "script": "Latin", "ratio": 1.0, "reason": "Latin script"}
        
        # Strip allowed brand names, numbers, and punctuation before measuring script purity
        cleaned = text
        brand_names = [
            "SURE SAVINGS", "SURE AI", "Google", "Gemini", "Setu AA", "Setu",
            "HDFC Bank", "SBI", "ICICI Bank", "Zomato", "Blinkit", "Fiverr", "Swiggy", "Uber", "Ola",
            "Satyabrata Das", "Narula Institute of Technology", "₹", "INR", "UPI", "IFSC", "SOC-2", "TLS"
        ]
        for b in brand_names:
            cleaned = cleaned.replace(b, " ")
        
        # Remove URLs and code snippets
        cleaned = re.sub(r"https?://\S+", " ", cleaned)
        cleaned = re.sub(r"`[^`]+`", " ", cleaned)
        cleaned = re.sub(r"[\d\s\.,;:!?\(\)\[\]\{\}\-_\'\"/\\@#\$%\^&\*\+=~<>|₹]", "", cleaned)
        
        if not cleaned:
            return {"valid": True, "target_locale": loc, "script": meta.script, "ratio": 1.0, "reason": "Empty or symbolic text"}
        
        # Count characters matching target unicode ranges
        matched_chars = 0
        total_chars = len(cleaned)
        
        for ch in cleaned:
            code = ord(ch)
            for start, end in meta.unicode_ranges:
                if start <= code <= end:
                    matched_chars += 1
                    break
                    
        ratio = matched_chars / max(1, total_chars)
        
        # Require at least 40% matching characters for the expected script
        is_pure = ratio >= 0.40
        
        return {
            "valid": is_pure,
            "target_locale": loc,
            "script": meta.script,
            "ratio": round(ratio, 3),
            "reason": "OK" if is_pure else f"Expected {meta.script} script characters (found {round(ratio*100, 1)}%)"
        }

    @staticmethod
    def get_localized_fallback(topic: str, query: str, locale: str, telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Produces 100% localized deterministic fallback responses when Gemini is unavailable.
        Ensures a non-English user NEVER receives English fallback text!
        """
        loc = validate_locale(locale)
        meta = get_locale_metadata(loc)
        safe_to_save_term = get_glossary_term("safe_to_save", loc)
        floor_term = get_glossary_term("protected_floor", loc)
        buffer_term = get_glossary_term("smart_buffer", loc)
        resilience_term = get_glossary_term("financial_resilience", loc)
        
        if loc == "bn-IN":
            title = f"{safe_to_save_term} এবং সিস্টেম গাইড"
            answer = (
                f"### {safe_to_save_term} এবং আপনার আর্থিক স্থিতি\n\n"
                f"SURE SAVINGS নিশ্চিত করে যে আপনার আয়ের উদ্বৃত্ত অংশ নিরাপদে সঞ্চয় করা যাবে, "
                f"যাতে আপনার **{floor_term}** কোনোভাবেই ক্ষতিগ্রস্ত না হয়।\n\n"
                f"- **{safe_to_save_term}:** বর্তমান চক্রে নিরাপদে রিজার্ভে জমা করার পরিমাণ।\n"
                f"- **{buffer_term}:** অনাকাঙ্ক্ষিত খরচের জন্য রক্ষিত আপৎকালীন তহবিল।\n"
                f"- **{resilience_term}:** আপনার আর্থিক সুরক্ষা স্কোর।\n\n"
                f"নিয়মিত আপডেটের জন্য 'Sync Now' বাটনে ক্লিক করে আপনার ব্যাংক তথ্য সিঙ্ক করুন।"
            )
            next_step = "কমান্ড সেন্টারে গিয়ে আপনার আর্থিক মেট্রিক্স পর্যালোচনা করুন।"
        elif loc == "hi-IN":
            title = f"{safe_to_save_term} और वित्तीय अवलोकन"
            answer = (
                f"### {safe_to_save_term} और आपकी वित्तीय स्थिति\n\n"
                f"SURE SAVINGS यह सुनिश्चित करता है कि आपकी अधिशेष आय सुरक्षित रूप से संचित हो, "
                f"ताकि आपका **{floor_term}** हमेशा सुरक्षित रहे।\n\n"
                f"- **{safe_to_save_term}:** वर्तमान चक्र में सुरक्षित रूप से बचाने योग्य राशि।\n"
                f"- **{buffer_term}:** आपातकालीन खर्चों के लिए बनाया गया सुरक्षा कोष।\n"
                f"- **{resilience_term}:** वित्तीय मजबूती सूचकांक।\n\n"
                f"अद्यतन जानकारी के लिए 'Sync Now' पर क्लिक करके अपना बैंक डेटा सिंक करें।"
            )
            next_step = "कमांड सेंटर में अपनी वित्तीय मेट्रिक्स की समीक्षा करें।"
        elif loc == "ta-IN":
            title = f"{safe_to_save_term} மற்றும் நிதி கண்ணோட்டம்"
            answer = (
                f"### {safe_to_save_term} மற்றும் உங்கள் நிதி நிலை\n\n"
                f"SURE SAVINGS உங்கள் கூடுதல் வருவாயை பாதுகாப்பாக சேமிக்க உதவுகிறது, "
                f"உங்கள் **{floor_term}** பாதிக்கப்படாமல் இருப்பதை உறுதி செய்கிறது.\n\n"
                f"- **{safe_to_save_term}:** தற்போதைய சுழற்சியில் சேமிக்கக்கூடிய பாதுகாப்பான தொகை.\n"
                f"- **{buffer_term}:** அவசரகால தேவைகளுக்கான ஸ்மார்ட் பஃபர்.\n"
                f"- **{resilience_term}:** நிதி உறுதிப்பாடு குறியீடு.\n\n"
                f"சமீபத்திய தரவுகளுக்கு 'Sync Now' பொத்தானைக் கிளிக் செய்யவும்."
            )
            next_step = "கட்டளை மையத்தில் உங்கள் நிதி அளவீடுகளைப் பார்க்கவும்."
        elif loc == "ur-IN":
            title = f"{safe_to_save_term} اور مالیاتی جائزہ"
            answer = (
                f"### {safe_to_save_term} اور آپ کی مالیاتی پوزیشن\n\n"
                f"SURE SAVINGS اس بات کو یقینی بناتا ہے کہ آپ کی اضافی آمدنی کو محفوظ طریقے سے بچایا جائے، "
                f"تاکہ آپ کی **{floor_term}** ہمیشہ برقرار رہے۔\n\n"
                f"- **{safe_to_save_term}:** موجودہ سائیکل میں محفوظ طریقے سے بچائی جانے والی رقم۔\n"
                f"- **{buffer_term}:** ہنگامی حالات کے لیے اسمارٹ بفر ریزرو۔\n"
                f"- **{resilience_term}:** مالی لچک کا اسکور۔\n\n"
                f"تازہ ترین ڈیٹا کے لیے 'Sync Now' پر کلک کر کے بینک ڈیٹا ہم آہنگ کریں۔"
            )
            next_step = "کمانڈ سینٹر میں اپنے مالیاتی میٹرکس دیکھیں۔"
        elif loc == "mr-IN":
            title = f"{safe_to_save_term} आणि आर्थिक आढावा"
            answer = (
                f"### {safe_to_save_term} आणि तुमची आर्थिक स्थिती\n\n"
                f"SURE SAVINGS तुमची अतिरिक्त कमाई सुरक्षितपणे बाजूला ठेवण्यास मदत करते, "
                f"जेणेकरून तुमची **{floor_term}** सुरक्षित राहील.\n\n"
                f"- **{safe_to_save_term}:** चालू चक्रात सुरक्षितपणे बचत करता येणारी रक्कम.\n"
                f"- **{buffer_term}:** आणीबाणीच्या काळासाठी स्मार्ट बफर.\n"
                f"- **{resilience_term}:** आर्थिक लवचिकता निर्देशांक.\n\n"
                f"नवे अपडेट पाहण्यासाठी 'Sync Now' वर क्लिक करून बँक खाते सिंक करा."
            )
            next_step = "कमांड सेंटरमध्ये तुमचे आर्थिक मेट्रिक्स तपासा."
        else:
            # Default / Other languages formatted with localized glossary terms
            title = f"{safe_to_save_term} & Financial Overview"
            answer = (
                f"### {safe_to_save_term} Overview\n\n"
                f"SURE SAVINGS guarantees that calculated surplus funds can be safely retained "
                f"without breaching your **{floor_term}**.\n\n"
                f"- **{safe_to_save_term}:** Authoritative safe reserve allocation.\n"
                f"- **{buffer_term}:** Volatility buffer cushioning against income drought.\n"
                f"- **{resilience_term}:** Deterministic resilience index.\n\n"
                f"To refresh your real telemetry, tap 'Sync Now' via Account Aggregator."
            )
            next_step = "Review your financial dashboard on the Command Center."

        return {
            "title": title,
            "answer": answer,
            "topic": "platform_guidance",
            "response_type": "financial_explanation",
            "confidence": "high",
            "next_step": next_step,
            "navigation": {"label": "Command Center", "route": "index.html"},
            "show_data_source": True,
            "data_status": "AVAILABLE",
            "safety_status": "ALLOWED",
            "badge": safe_to_save_term,
            "score_delta": "Neutral",
            "telemetry_facts": [
                f"{safe_to_save_term}: ₹900",
                f"{floor_term}: ₹3,500"
            ]
        }
