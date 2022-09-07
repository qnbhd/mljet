import type { NextPage } from 'next'
import { useEffect } from 'react'
import GitHubButton from 'react-github-btn'
import hljs from 'highlight.js';
import { Container } from '../components/Container'

import javascript from 'highlight.js/lib/languages/javascript';
import 'highlight.js/styles/github.css'

const Home: NextPage = () => {

  useEffect(() => {
    hljs.registerLanguage('javascript', javascript);
    hljs.highlightAll();

  }, [])

  return (
    <>
      <Container size='full' className='bg-gradient-to-b from-[#1CF1CC] to-[#EA6CFF]'>
        <Container size='lg' className='flex w-full justify-center items-center py-10 h-screen md:h-[700px]'>
          <div className='grid gap-10 grid-cols-1 md:grid-cols-2'>

            <div className='w-full h-full flex items-center'>
              <div>
                <h1 className='text-4xl md:text-6xl font-black'> DeployMe </h1>
                <h2 className='text-xl mt-6'> Minimalistic ML auto-deployment tool. </h2>

                <div className='flex mt-6'>
                  <div className='mr-4'>
                    <GitHubButton href="https://github.com/qnbhd/deployme" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star on GitHub">Star</GitHubButton>
                  </div>
                  <GitHubButton href="https://github.com/qnbhd/deployme/fork" data-icon="octicon-repo-forked" data-size="large" data-show-count="true" aria-label="Fork on GitHub">Fork</GitHubButton>
                </div>
              </div>
            </div>



          </div>
        </Container>
      </Container>


      <Container size='full' className='bg-chick'>
        <Container className='flex flex-col justify-center items-center pt-5 pb-7'>
          <p className='mb-2 text-xs'> Built in  </p>
          <img src='/imgs/ai-product-hack/itmo.svg' className='w-48' />
        </Container>
      </Container>

      <Container size='full' className='bg-prim text-slate-100'>
        <Container size='lg' className='py-20'>
          <h2 className='font-bold text-3xl'> Why? </h2>

          <div className='grid grid-cols-1 md:grid-cols-[100%_1fr] gap-10'>
            <p className='mt-6'>
                DeployMe is a tool that allows you to deploy your ML models with a single click.

              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc justo mi, rhoncus sit amet finibus a, facilisis a magna. Nullam lobortis eget dui non scelerisque. Praesent ac maximus nulla. Etiam vitae urna ac leo gravida pretium vel et leo. Donec nec mi sed quam lobortis lacinia. Quisque dictum enim nec est iaculis efficitur. Maecenas sed dolor vitae nibh cursus congue. Sed tempor urna vel arcu laoreet pulvinar. Vestibulum ultrices congue ipsum eget tristique. Nulla facilisi. Donec vehicula efficitur odio. Suspendisse sodales dui non urna accumsan egestas. Morbi ut consequat ex. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Curabitur in odio libero. Donec lobortis mi et tortor mollis venenatis.


            </p>

          </div>
        </Container>

        <Container size='lg' className='border-t-2 border-white py-20'>
          <h2 className='font-bold text-3xl'> Quickstart </h2>

          <div>
            <h3 className='font-bold text-2xl my-10'> Install DeployMe </h3>
            <pre className="shell">
<code>
pip install deployme
</code>
</pre>

            <h3 className='font-bold text-2xl my-10'> Make your ML model. </h3>
            <pre className="js">
              <code>
                {`automl = TabularAutoML(
    task=task,
    timeout=TIMEOUT,
    cpu_limit=N_THREADS,
    reader_params={
        "n_jobs": N_THREADS,
        "cv": N_FOLDS,
        "random_state": RANDOM_STATE,
    },
)

oof_pred = automl.fit_predict(tr_data, roles=roles, verbose=1)`}
              </code>
            </pre>

            <h3 className='font-bold text-2xl my-10'> Deploy your model </h3>
            <pre>
              <code className="js rounded-lg">
                {`deploy_to_docker(model=automl, image_name="my_lama_service")`}
              </code>
            </pre>

            <h3 className='font-bold text-2xl my-10'> Open the browser :)  </h3>
          </div>

          <div className='text-center mt-20'>
            <a href='#' className='text-violet-100 bg-chick hover:bg-super-hover px-6 py-3 font-bold text-xl rounded-md'>
              Read the full docs
            </a>
          </div>
        </Container>
      </Container>
    </>
  )
}

export default Home
