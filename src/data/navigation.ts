export interface NavItem {
  label: string;
  href: string;
  children?: { label: string; href: string }[];
}

export const mainNavigation: NavItem[] = [
  { label: 'Home', href: '/' },
  {
    label: 'Slaapkamer',
    href: '/slaapkamer/',
    children: [
      { label: 'Luxe boxspring', href: '/beste-luxe-boxspring/' },
      { label: 'Donzen dekbed', href: '/beste-donzen-dekbed/' },
      { label: 'Matras 120×200', href: '/beste-matras-120x200/' },
      { label: 'Molton hoeslaken', href: '/beste-molton-hoeslaken/' },
      { label: 'Hoeslaken 180×200', href: '/beste-hoeslaken-180x200/' },
      { label: '4 seizoenen dekbed', href: '/beste-4-seizoenen-dekbed/' },
      { label: 'Traagschuim kussen', href: '/beste-traagschuim-kussen/' },
      { label: 'Dekbedovertrek 240×220', href: '/beste-dekbedovertrek-240x220/' },
      { label: 'Mobiele airco slaapkamer', href: '/beste-mobiele-airco-slaapkamer/' },
      { label: 'Flanellen dekbedovertrek', href: '/beste-flanellen-dekbedovertrek/' },
    ],
  },
  {
    label: 'Interieur',
    href: '/interieur/',
    children: [
      { label: 'Grote zitzak', href: '/beste-grote-zitzak/' },
      { label: 'Tv meubel eiken', href: '/beste-tv-meubel-eiken/' },
      { label: 'Grote hanglamp', href: '/beste-grote-hanglamp/' },
      { label: 'Hangstoel binnen', href: '/beste-hangstoel-binnen/' },
      { label: 'Kleine houtkachel', href: '/beste-kleine-houtkachel/' },
      { label: 'Open boekenkast', href: '/beste-open-boekenkast/' },
      { label: 'Plafond ventilator', href: '/beste-plafond-ventilator/' },
      { label: 'Zwevend tv meubel', href: '/beste-zwevend-tv-meubel/' },
      { label: 'Poef met opbergruimte', href: '/beste-poef-met-opbergruimte/' },
      { label: 'Elektrische kachel woonkamer', href: '/beste-elektrische-kachel-woonkamer/' },
    ],
  },
  {
    label: 'Wasruimte',
    href: '/wasruimte/',
    children: [
      { label: 'Droogtoren', href: '/beste-droogtoren/' },
      { label: 'Droogloopmat', href: '/beste-droogloopmat/' },
      { label: 'Rieten wasmand', href: '/beste-rieten-wasmand/' },
      { label: 'Droogrek hangend', href: '/beste-droogrek-hangend/' },
      { label: 'Warmtepompdroger', href: '/beste-warmtepompdroger/' },
      { label: 'Elektrische droogrek', href: '/beste-elektrische-droogrek/' },
      { label: 'Badkamer ventilator', href: '/beste-badkamer-ventilator/' },
      { label: 'Douchekop met slang', href: '/beste-douchekop-met-slang/' },
      { label: 'Wasmand met deksel', href: '/beste-wasmand-met-deksel/' },
      { label: 'Kledingkast met schuifdeuren', href: '/beste-kledingkast-met-schuifdeuren/' },
    ],
  },
  { label: 'Over ons', href: '/over-ons/' },
];
