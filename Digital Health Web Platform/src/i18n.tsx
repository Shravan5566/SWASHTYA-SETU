import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

type Lang = 'en' | 'mr'

const mr: Record<string, string> = {
  // Navigation & Platform Branding
  'nav.apply': 'आरोग्य कार्ड नोंदणी',
  'nav.track': 'अर्जाची स्थिती',
  'nav.network': 'क्लिनिक व प्रभाग',
  'nav.privacy': 'DPDP गोपनीयता',
  'nav.staff': 'कर्मचारी लॉगिन',
  'pmc': 'पुणे आरोग्य विभाग',
  'pmc.tag': 'पुणे नागरी आरोग्य यंत्रणा',
  'tagline': 'स्कॅन • उपचार • समन्वय',

  // Roles
  'role.doctor': 'वैद्यकीय अधिकारी (Doctor)',
  'role.pharmacist': 'औषध निर्माण अधिकारी (Pharmacist)',
  'role.health': 'साथरोग नियंत्रण तज्ज्ञ (Epidemiologist)',
  'role.admin': 'मुख्य सुरक्षा अधिकारी (Admin)',

  // Hero Section
  'hero.h1a': 'डिजिटल आरोग्य ओळखपत्र',
  'hero.h1b': 'व नागरी आरोग्य सेवा प्रणाली.',
  'hero.sub':
    'पुणे महानगरपालिका प्रभागांमधील नागरिक, वैद्यकीय तज्ज्ञ आणि सार्वजनिक आरोग्य यंत्रणेला जोडणारी एकात्मिक डिजिटल आरोग्य प्रणाली — रुग्णांच्या पूर्ण संमतीने व गोपनीयतेने संचलित.',
  'cta.apply': 'डिजिटल आरोग्य कार्डसाठी अर्ज करा',
  'cta.track': 'अर्जाची सद्यस्थिती तपासा',

  // Stats Highlights
  'stat.wards': '१५ प्रभाग',
  'stat.wards.sub': 'रोग नियंत्रण ग्रीड',
  'stat.otp': 'संमती OTP',
  'stat.otp.sub': 'रुग्ण-नियंत्रित डेटा',
  'stat.qr': 'QR ओळख',
  'stat.qr.sub': 'तात्काळ ओपीडी नोंदणी',

  // Pillars Architecture
  'pillars': 'प्लॅटफॉर्मची मुख्य संरचना',
  'pillars.h2': 'वैद्यकीय गोपनीयता आणि जलद उपचारांसाठी सक्षम',
  'p1.t': 'वैद्यकीय ओपीडी व क्लिनिकल कक्ष',
  'p1.d':
    'QR कार्ड स्कॅन आणि ६-अंकी रुग्ण संमती OTP सह त्वरित प्रवेश. रुग्णाचा संपूर्ण वैद्यकीय इतिहास, औषध सूची आणि ॲलर्जी सुरक्षा सूचना एकाच ठिकाणी उपलब्ध.',
  'p2.t': 'औषध वितरण व गोपनीयता कक्ष',
  'p2.d':
    'काटेकोर डेटा विलगीकरण: औषध विक्रेत्यास केवळ औषध, प्रमाण आणि कार्ड क्रमांक दिसतो. रुग्णाचे वैयक्तिक आजार आणि निदान नोंदी कूटबद्ध (Encrypted) व सुरक्षित.',
  'p3.t': 'सार्वजनिक आरोग्य व महामारी नियंत्रण रडार',
  'p3.d':
    'पुण्यातील १५ प्रभागांमध्ये साथरोगांचा वेळेत अंदाज घेण्यासाठी २-सिग्मा गणितीय विश्लेषण प्रणाली; नागरिकांची ओळख सुरक्षित ठेवून उद्रेक इशारा.',
  'p4.t': 'वैद्यकीय इतिहास व डिजिटल सारांश',
  'p4.d':
    'रुग्णाच्या मान्यतेने (OTP) तयार होणारा सुरक्षित तपासणी इतिहास आणि औषधोपचार सारांश, पुढील उपचारांसाठी त्वरित उपलब्ध.',
  'enter.terminal': 'पोर्टल उघडा',

  // Royal 3D Card
  'card.title': 'डिजिटल आरोग्य ओळख',
  'card.badge': 'सुरक्षित QR ओळख',
  'card.citizen': 'नागरीक QR कार्ड',
  'card.issue': 'कार्ड जारी करा',

  // Application & Forms
  'step.1': 'नागरिक ओळख',
  'step.2': 'आरोग्य व प्रभाग',
  'step.3': 'तपासणी व पुष्टी',
  'f.name': 'पूर्ण नाव (शासकीय ओळखपत्रानुसार)',
  'f.phone': 'मोबाईल क्रमांक',
  'f.dob': 'जन्मतारीख',
  'f.locality': 'पुणे प्रभाग / परिसर',
  'f.blood': 'रक्तगट',
  'f.allergy': 'औषध किंवा इतर ॲलर्जी',
  'f.chronic': 'दीर्घकालीन आजार (उदा. मधुमेह, उच्च रक्तदाब)',
  'next': 'पुढील पायरी',
  'back': 'मागील पायरी',
  'submit': 'अर्ज सादर करा',
  'save': 'आरोग्य कार्ड डाउनलोड / प्रिंट करा',

  // Doctor & OPD Portal
  'scan.upload': 'QR कार्ड प्रतिमा अपलोड करा',
  'scan.verify': 'कार्ड पडताळा',
  'otp.title': 'रुग्ण संमती पडताळणी (Consent Gate)',
  'otp.verify': 'OTP द्वारे प्रमाणीकरण करा',
  'dictate': 'व्हॉइस प्रिस्क्रिप्शन (बोलून नोंदवा)',
  'listen': 'प्रिस्क्रिप्शन ऑडिओ ऐका',
  'lock': '२४ तासांनंतर नोंद लॉक होईल',

  // Pharmacist Terminal
  'priv.banner':
    'डेटा गोपनीयता सक्रिय: रुग्णाचा पूर्व वैद्यकीय इतिहास आणि निदान नोंदी औषध कक्षापासून सुरक्षित आणि कूटबद्ध (Encrypted) ठेवण्यात आल्या आहेत.',
  'dispense': 'औषध वितरण नोंदवा',
  'restricted': 'शेड्यूल H औषध — अधिकृत डॉक्टरांच्या ताज्या संमतीशिवाय वितरण प्रतिबंधित',

  // Public Health Surveillance & Admin
  'wards': 'निरीक्षणाखालील प्रभाग',
  'cases': 'एकूण नोंद झालेले रुग्ण',
  'spikes': 'सक्रिय उद्रेक इशारे (Spikes)',
  'insufficient': '< ५ (अपुरा डेटा)',
  'anomaly': '२-सिग्मा रोग उद्रेक विसंगती आढळली',
  'approve': 'मंजूर करा व कार्ड जारी करा',
  'reject': 'अस्वीकृत करा',
  'audit': 'अपरिवर्तनीय डिजिटल ऑडिट नोंद',
}

const en: Record<string, string> = {}

const Ctx = createContext<{
  lang: Lang
  setLang: (l: Lang) => void
  t: (k: string, fallback: string) => string
}>(null as any)

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(
    () => (localStorage.getItem('ss-lang') as Lang) || 'en'
  )

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const set = (l: Lang) => {
    localStorage.setItem('ss-lang', l)
    document.documentElement.lang = l
    setLang(l)
  }

  const t = (k: string, fb: string) => (lang === 'mr' ? mr[k] ?? fb : en[k] ?? fb)

  return <Ctx.Provider value={{ lang, setLang: set, t }}>{children}</Ctx.Provider>
}

export const useLang = () => useContext(Ctx)
