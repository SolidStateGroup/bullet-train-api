import * as React from 'react'
import { SVGProps } from 'react'
const DropIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={55}
    height={54}
    fill='none'
    viewBox='0 0 55 54'
    {...props}
  >
    <path
      fill='#9DA4AE'
      fillRule='evenodd'
      d='M27.5 6.75c5.914 0 11.126 3.737 13.005 9.101 5.59.745 9.911 5.46 9.911 11.149 0 2.747-1.017 5.39-2.864 7.445a2.312 2.312 0 0 1-1.72.76c-.538 0-1.078-.184-1.516-.562a2.227 2.227 0 0 1-.2-3.18A6.665 6.665 0 0 0 45.833 27c0-3.722-3.085-6.75-6.875-6.75h-.23c-1.09 0-2.03-.756-2.245-1.807-.857-4.167-4.634-7.193-8.983-7.193-4.348 0-8.127 3.026-8.982 7.193-.215 1.05-1.157 1.807-2.248 1.807h-.229c-3.79 0-6.875 3.028-6.875 6.75 0 1.647.61 3.235 1.719 4.464a2.227 2.227 0 0 1-.202 3.179 2.321 2.321 0 0 1-3.233-.198A11.114 11.114 0 0 1 4.583 27c0-5.688 4.322-10.404 9.911-11.149C16.376 10.487 21.587 6.75 27.5 6.75Zm-1.593 18.63c.903-.846 2.33-.84 3.213.03l6.875 6.75c.896.879.896 2.301 0 3.18a2.307 2.307 0 0 1-1.62.66c-.587 0-1.173-.22-1.62-.66l-2.963-2.909V45c0 1.244-1.027 2.25-2.292 2.25s-2.292-1.006-2.292-2.25V32.301l-2.99 2.835a2.32 2.32 0 0 1-3.24-.056 2.221 2.221 0 0 1 .054-3.182l6.875-6.518Z'
      clipRule='evenodd'
    />
  </svg>
)
export default DropIcon