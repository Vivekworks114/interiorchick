export interface CardItem {
  title: string;
  href: string;
  image: string;
  alt: string;
}

export const heroContent = {
  title: 'Dé interieursite voor vrouwen',
  description:
    'Bij InterieurChick.nl kun je terecht om inspiratie op te doen voor de inrichting van jouw huis. Met inzichtelijke blogs geschreven door interieurdesigners, leer jij op welke aspecten je kunt letten bij je eigen interieur opstelling. Bovendien vind je bij ons verschillende top 10 lijstjes zodat jij je woning kunt opwaarderen met het mooiste en beste interieur.',
  backgroundImage: '/images/2023/01/Group-8031.jpg',
};

export const categoryLinks = [
  {
    label: 'TV',
    href: '/beste-tv/',
    icon: '/images/2023/01/icon-park-outline_plug-one.svg',
  },
  {
    label: 'Zwevend tv meubel',
    href: '/beste-zwevend-tv-meubel/',
    icon: '/images/2023/01/icon-park-outline_sofa.svg',
  },
  {
    label: 'Badkamer ventilator',
    href: '/beste-badkamer-ventilator/',
    icon: '/images/2023/01/icon-park-outline_four-leaves.svg',
  },
  {
    label: 'Bewegingssensoren',
    href: '/beste-bewegingssensoren/',
    icon: '/images/2023/01/icon-park-outline_color-filter.svg',
  },
  {
    label: 'Kleine houtkachel',
    href: '/beste-kleine-houtkachel/',
    icon: '/images/2023/01/icon-park-outline_great-wall.svg',
  },
  {
    label: 'Bartafel met krukken',
    href: '/beste-bartafel-met-krukken/',
    icon: '/images/2023/01/icon-park-outline_floor-tile.svg',
  },
] as const;

export const topTenSection = {
  title: 'Top 10 lijstjes',
  description:
    'Op zoek naar kwalitatief hoogwaardige en mooie meubels voor in je woning? Wil je bovendien de keus hebben tussen verschillende prijsklassen? Bekijk dan onze top 10 lijstjes.',
};

export const topTenCards: CardItem[] = [
  {
    title: 'Digitale wekker',
    href: '/beste-digitale-wekker/',
    image: '/images/2023/06/digitale-wekker.jpeg',
    alt: 'digitale wekker',
  },
  {
    title: 'Rieten wasmand',
    href: '/beste-rieten-wasmand/',
    image: '/images/2023/06/rieten-wasmand.jpeg',
    alt: 'rieten wasmand',
  },
  {
    title: 'Douchekop met slang',
    href: '/beste-douchekop-met-slang/',
    image: '/images/elementor/thumbs/douchekop-rgc2amqkxw50cqfhrpedps5nj85rljcknedu1goguw.jpg',
    alt: 'douchekop',
  },
  {
    title: 'Zwevend tv meubel',
    href: '/beste-zwevend-tv-meubel/',
    image: '/images/2023/06/zwevend-tv-meubel.jpeg',
    alt: 'zwevend tv meubel',
  },
  {
    title: 'Droogtoren',
    href: '/beste-droogtoren/',
    image: '/images/2023/06/droogtoren.jpeg',
    alt: 'droogtoren',
  },
  {
    title: 'Grote zitzak',
    href: '/beste-grote-zitzak/',
    image: '/images/2025/12/zitzak-2-1024x682.jpg',
    alt: 'zitzak',
  },
];

export const quoteSection = {
  title: '"De inrichting van je woning representeert jouw persoonlijkheid."',
  backgroundImage: '/images/2023/01/Group-8131.jpg',
};

export const reviewsSection = {
  title: 'Producten reviews',
  description:
    'Ontdek de magie van interieurproducten door middel van betoverende reviews. Van knusse kussens tot trendy tapijten en elegante verlichting, onze deskundige beoordelingen brengen het interieur tot leven. Laat je inspireren en vind de perfecte stukken om je huis te transformeren in een stijlvol toevluchtsoord.',
};

export const ctaSection = {
  description:
    'Op InteriorChick.nl vind je de beste reviews van de meest populaire artikelen op het gebied van interieur en design. Wacht dus niet langer en kijk snel welke items niet mogen ontbreken in jouw huis! Mocht je vragen hebben, neem dan contact op via onderstaande knop.',
  ctaLabel: 'Contact opnemen',
  ctaHref: '/contact/',
};

export const latestReviews: CardItem[] = [
  {
    title: 'Tv',
    href: '/beste-tv/',
    image: '/images/2023/06/tv.jpeg',
    alt: 'tv',
  },
  {
    title: 'Poef met opbergruimte',
    href: '/beste-poef-met-opbergruimte/',
    image: '/images/2023/06/poef-met-opbergruimte.jpeg',
    alt: 'poef met opbergruimte',
  },
  {
    title: 'Hangstoel binnen',
    href: '/beste-hangstoel-binnen/',
    image: '/images/2023/06/hangstoel-binnen-1.jpeg',
    alt: 'hangstoel binnen',
  },
  {
    title: 'Plafond ventilator',
    href: '/beste-plafond-ventilator/',
    image: '/images/2023/06/plafond-ventilator.jpeg',
    alt: 'plafond ventilator',
  },
  {
    title: 'Matras 120x200',
    href: '/beste-matras-120x200/',
    image: '/images/2023/06/matras-120-x-200.jpeg',
    alt: 'matras 120x200',
  },
  {
    title: 'Satijnen kussensloop',
    href: '/beste-satijnen-kussensloop/',
    image: '/images/2023/06/satijnen-kussensloop.jpeg',
    alt: 'satijnen kussensloop',
  },
];
