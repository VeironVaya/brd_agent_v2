export const DIRECTORATE_OPTIONS = [
  'CEO Office',
  'Marketing',
  'Sales',
  'Planning & Transformation (P&T)',
  'Finance & Risk Management',
  'Network',
  'Information Technology (IT)',
  'Human Capital Management (HCM)',
]

export const CHOICE_SECTIONS = {
  '1.3': {
    title: 'Purpose of this Business Requirement',
    groups: {
      selected: {
        label: 'Purpose',
        options: [
          'BR to enhance existing service/application/process',
          'BR to terminate existing service/application/process',
          'BR for new service/application/process',
          'BR to replace existing service/application/process',
          'Others, please specify',
        ],
        multiple: true,
      },
    },
  },
  '1.4': {
    title: 'Program Type',
    groups: {
      selected: {
        label: 'If IT-led / IT-driven program',
        options: [
          'Automation', 'Audit compliance', 'Business engagement model', 'Capacity expansion', 'Cloud',
          'Digital ways of working', 'End of life replacement', 'End of Support (EoS)', 'Infrastructure',
          'License renewal', 'Integration / Modernization', 'Security compliance', 'Security enhancement',
          'Others, please specify',
        ],
        multiple: true,
      },
    },
  },
  '3.2': {
    title: 'Product / Service Specification',
    groups: {
      target_market_segmentation: {
        label: 'Target market segmentation',
        options: ['HVC', 'Non-HVC', 'SME', 'Corporate', 'Governance', 'Targeted segment, please specify'],
        multiple: true,
      },
      subscriber_eligibility: {
        label: 'Subscriber eligibility',
        options: ['Telkomsel customer', 'Telkomsel employee', 'Others, please specify'],
        multiple: true,
      },
      brand_eligibility: {
        label: 'Brand eligibility',
        options: ['simPATI', 'KartuAS', 'Loop', 'ByU', 'Others'],
        multiple: true,
      },
      channel_eligibility: {
        label: 'Channel eligibility',
        options: [
          'Self service channel', 'Assisted channel', 'UMB, please specify ADN', 'SMS, please specify ADN',
          'Web, please specify', 'Walk-in', 'Call-in', 'Mobile apps, please specify', '3rd party channels, please specify',
        ],
        multiple: true,
      },
      area_coverage: {
        label: 'Area coverage',
        options: ['National-wide', 'Selected area, please specify'],
        multiple: false,
      },
      terms_and_conditions: {
        label: 'Product / Service Terms and Conditions',
        options: [
          'Customer restriction / limitation to purchase / register the product',
          'Eligible time period for customer to purchase / register this product/service',
          'Product / service compatibility and correlation with other product / service',
        ],
        multiple: true,
      },
    },
  },
}

export function isChoiceSection(sectionId) {
  return !!CHOICE_SECTIONS[sectionId]
}