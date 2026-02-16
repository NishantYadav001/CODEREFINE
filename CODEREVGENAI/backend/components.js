/**
 * Unified UI/UX Component Library
 * Enforces consistent "DNA" (border-radius, shadows, transitions) across the app.
 */

export const Components = {
    // Standard Button with variants
    Button: ({ text, onClick, variant = 'primary', icon, type = 'button', extraClasses = '' }) => {
        const base = "inline-flex items-center justify-center px-4 py-2 border text-sm font-medium rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200";
        
        const variants = {
            primary: "border-transparent text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500",
            secondary: "border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-700",
            danger: "border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-500",
            ghost: "border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 shadow-none"
        };

        const iconHtml = icon ? `<i class="${icon} mr-2 -ml-1"></i>` : '';
        
        return `
            <button type="${type}" onclick="${onClick}" class="${base} ${variants[variant]} ${extraClasses}">
                ${iconHtml}${text}
            </button>
        `;
    },

    // Standard Input Field
    Input: ({ id, type = 'text', placeholder = '', label, value = '' }) => {
        const labelHtml = label ? `<label for="${id}" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">${label}</label>` : '';
        return `
            <div class="mb-4">
                ${labelHtml}
                <input type="${type}" id="${id}" name="${id}" class="input-std shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-lg" placeholder="${placeholder}" value="${value}">
            </div>
        `;
    },

    // Standard Card Container
    Card: ({ title, content, footer, extraClasses = '' }) => {
        return `
            <div class="card-std overflow-hidden ${extraClasses}">
                ${title ? `
                <div class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">${title}</h3>
                </div>` : ''}
                <div class="px-4 py-5 sm:p-6">
                    ${content}
                </div>
                ${footer ? `
                <div class="px-4 py-4 sm:px-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
                    ${footer}
                </div>` : ''}
            </div>
        `;
    }
};