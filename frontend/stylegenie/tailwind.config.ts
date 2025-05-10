import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";
import plugin from "tailwindcss/plugin";

export default {
	darkMode: "class",
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
		"./styles/**/*.{css,ts}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			colors: {
				'white': 'rgb(255 255 255 / var(--tw-bg-opacity, 1))',
				// 'text-primary': '#6000d6e6',
				'text-primary': '##8B5DFF',
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					// DEFAULT: '#6000d6e6 !important',
					DEFAULT: '#8B5DFF !important',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				}
			},
			boxShadow: {
				'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
				'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
				'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
				'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
				'2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
				'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
				'none': '0 0 #0000',
			},
			fontWeight: {
				'thin': '100',
				'extralight': '200',
				'light': '300',
				'normal': '400',
				'medium': '500',
				'semibold': '600',
				'bold': '700',
				'extrabold': '800',
				'black': '900',
			},
			fontSize: {
				'sm': '0.875rem',
				'base': '1rem',
				'lg': '1.125rem',
				'xl': '1.25rem',
				'2xl': '1.5rem',
				'3xl': '1.875rem',
				'4xl': '2.25rem',
				'5xl': '3rem',
				'6xl': '3.75rem',
				'7xl': '4.5rem',
				'8xl': '6rem',
				'9xl': '8rem',
			},
			lineHeight: {
				'sm': '1.25rem',
				'base': '1.5rem',
				'lg': '1.75rem',
				'xl': '1.75rem',
				'2xl': '2rem',
				'3xl': '2.25rem',
				'4xl': '2.5rem',
				'5xl': '1',
				'6xl': '1',
				'7xl': '1',
				'8xl': '1',
				'9xl': '1',
			},
			opacity: {
				'0': '0',
				'5': '0.05',
				'10': '0.1',
				'20': '0.2',
				'25': '0.25',
				'30': '0.3',
				'40': '0.4',
				'50': '0.5',
				'60': '0.6',
				'70': '0.7',
				'75': '0.75',
				'80': '0.8',
				'90': '0.9',
				'95': '0.95',
				'100': '1',
			},
			spacing: {
				'0': '0px',
				'1': '0.25rem',
				'2': '0.5rem',
				'3': '0.75rem',
				'4': '1rem',
				'5': '1.25rem',
				'6': '1.5rem',
				'8': '2rem',
				'10': '2.5rem',
				'12': '3rem',
				'16': '4rem',
				'20': '5rem',
				'24': '6rem',
				'32': '8rem',
				'40': '10rem',
				'48': '12rem',
				'56': '14rem',
				'64': '16rem',
			},
			borderColor: {
				DEFAULT: 'hsl(var(--border))',
			},
			fontFamily: {
				playfair: ['Playfair Display', 'serif'],
				montserrat: ['Montserrat', 'sans-serif'],
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				'fade-in': {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' }
				},
				'pulse-light': {
					'0%, 100%': { opacity: '1' },
					'50%': { opacity: '0.7' }
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'fade-in': 'fade-in 0.5s ease-out',
				'pulse-light': 'pulse-light 2s ease-in-out infinite'
			}
		}
	},
	plugins: [
		animate,
		plugin(({ addUtilities }: { addUtilities: (utilities: Record<string, Record<string, string>>) => void }) => {
			addUtilities({
				'.border-border': {
					borderColor: 'hsl(var(--border))',
					borderWidth: '1px',
				},
				'.bg-background': {
					backgroundColor: 'hsl(var(--background))',
				},
				'.bg-secondary': {
					backgroundColor:'hsl(var(--secondary) / 0.5) !important',
				},
				'.bg-secondary/50': {
					backgroundColor:'hsl(var(--secondary) / 0.5) !important',
				},
				'.border-primary/20': {
					borderColor: 'hsl(var(--primary) / 0.2)',
				},
				'.text-left': {
					textAlign: 'left !important',
				}
			});
		}),
	],
} satisfies Config;
