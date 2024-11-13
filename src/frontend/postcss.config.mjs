   /** @type {import('postcss-load-config').Config} */
   const config = {
    plugins: {
      tailwindcss: {},
    },
    map: process.env.NODE_ENV === 'development',
  };

  export default config;