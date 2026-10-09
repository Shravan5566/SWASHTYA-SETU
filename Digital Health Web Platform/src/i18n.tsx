import { createContext, useContext, useState, type ReactNode } from 'react'

type Lang = 'en' | 'mr'
const mr: Record<string, string> = {
  'nav.apply': 'आरोग्य कार्डसाठी अर्ज', 'nav.track': 'स्थिती तपासा', 'nav.network': 'क्लिनिक नेटवर्क', 'nav.privacy': 'DPDP गोपनीयता',
  'nav.staff': 'कर्मचारी लॉगिन', 'role.doctor': 'डॉक्टर', 'role.pharmacist': 'औषध विक्रेता', 'role.health': 'सार्वजनिक आरोग्य', 'role.admin': 'प्रशासक',
  'pmc': 'पुणे परिसर', 'tagline': 'स्कॅन • काळजी • एकत्र',
  'hero.h1a': 'डिजिटल आरोग्य ओळख', 'hero.h1b': 'आणि नागरिक आरोग्य जाळे.',
  'hero.sub': 'पुणे परिसरासाठी एकात्मिक डिजिटल आरोग्य सुविधा. जलद QR नोंदणी, रुग्ण संमतीने तपासणी आणि प्रभाग-स्तरीय साथ नियंत्रण.',
  'cta.apply': 'डिजिटल आरोग्य कार्डसाठी अर्ज करा', 'cta.track': 'अर्जाची स्थिती पहा',
  'pillars': 'चार आधारस्तंभ',
  'p1.t': 'डॉक्टर क्लिनिकल पोर्टल', 'p1.d': 'QR स्कॅन + ६-अंकी रुग्ण संमती OTP.',
  'p2.t': 'औषध वितरण', 'p2.d': 'काटेकोर ४-स्तंभ विलगीकरण; निदान नोंदी पूर्णपणे लपवलेल्या.',
  'p3.t': 'आरोग्य निरीक्षण', 'p3.d': '२-सिग्मा साथ विसंगती शोध, गोपनीयता संरक्षणासह.',
  'p4.t': 'क्लिनिकल सारांश', 'p4.d': 'रुग्ण संमतीने तयार होणारा क्लिनिकल सारांश.',
  'f.name': 'पूर्ण कायदेशीर नाव', 'f.phone': 'फोन नंबर', 'f.dob': 'जन्मतारीख', 'f.locality': 'पुणे परिसर', 'f.blood': 'रक्तगट', 'f.allergy': 'ज्ञात अ‍ॅलर्जी',
  'next': 'पुढे', 'back': 'मागे', 'submit': 'अर्ज सादर करा', 'save': 'फोनवर सेव्ह करा / कार्ड प्रिंट करा',
  'step.1': 'ओळख', 'step.2': 'आरोग्य', 'step.3': 'पुनरावलोकन',
  'scan.upload': 'QR कार्ड प्रतिमा अपलोड करा', 'scan.verify': 'पडताळा', 'otp.title': 'रुग्ण संमती', 'otp.verify': 'OTP पडताळा',
  'dictate': 'प्रिस्क्रिप्शन बोलून लिहा', 'listen': 'सारांश ऐका', 'lock': '२४ तासांनंतर लॉक',
  'priv.banner': 'गोपनीयता विलगीकरण सक्रिय: क्लिनिकल निदान नोंदी व रुग्ण इतिहास वितरण टर्मिनलपासून क्रिप्टोग्राफिकली लपवलेले आहेत.',
  'dispense': 'वितरित करा व नोंदवा', 'restricted': 'रिफिल प्रतिबंधित (शेड्यूल H) — डॉक्टरांची पुन्हा मंजुरी आवश्यक',
  'wards': 'निरीक्षणाखालील प्रभाग', 'cases': 'नोंदवलेली प्रकरणे', 'spikes': 'सक्रिय विसंगती',
  'insufficient': '< ५ (अपुरा डेटा)', 'anomaly': '२-सिग्मा विसंगती आढळली',
  'approve': 'मंजूर करा व कार्ड जारी करा', 'reject': 'कारणासह नाकारा',
  'audit': 'अपरिवर्तनीय ऑडिट नोंद',
}
const en: Record<string, string> = {}
const Ctx = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (k: string, fallback: string) => string }>(null as any)

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>((localStorage.getItem('ss-lang') as Lang) || 'en')
  const set = (l: Lang) => { localStorage.setItem('ss-lang', l); document.documentElement.lang = l; setLang(l) }
  const t = (k: string, fb: string) => (lang === 'mr' ? mr[k] ?? fb : en[k] ?? fb)
  return <Ctx.Provider value={{ lang, setLang: set, t }}>{children}</Ctx.Provider>
}
export const useLang = () => useContext(Ctx)
