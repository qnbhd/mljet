import type { AppProps } from 'next/app'
import { NavBar } from '../components/NavBar'
import { Footer } from '../components/Footer'
import { DefaultSeo } from 'next-seo'
import '../styles/globals.css'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <DefaultSeo
        title='🚀 Deployme'
        description='Minimalistic, open-source, self-hosted deployment platform for your ML projects.'
        defaultTitle='🚀 DeployMe'
        openGraph={{
          type: 'website',
          locale: 'en_IE',
          url: '#',
          site_name: 'DeployMe',
          description: 'Minimalistic, open-source, self-hosted deployment platform for your ML projects.',
          title: 'DeployMe',
          images: [
            {
              url: '/imgs/ray/raycast-untitled.svg',
              alt: 'DeployMe',
              height: 1080,
              width: 1920,
            }
          ]
        }}
      />
      <div className='w-full min-h-screen bg-slate-100 text-slate-100'>
        <NavBar />
        <Component {...pageProps} />
        <Footer />
      </div>
    </>
  );
}

export default MyApp
