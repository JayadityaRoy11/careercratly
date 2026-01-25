export default function Home() {
  return (
    <main className="min-h-screen bg-[#F5F7FA] text-[#1F2933]">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white shadow">
        <h1 className="text-2xl font-bold text-[#0A2540]">ResumeIQ</h1>
        <button className="px-4 py-2 bg-[#FF9F43] text-white rounded-lg">
          Upload Resume
        </button>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center text-center px-6 py-20">
        <h2 className="text-4xl md:text-5xl font-bold text-[#0A2540] max-w-3xl">
          Build an ATS-Friendly Resume. Get Hired Faster.
        </h2>
        <p className="mt-6 text-lg max-w-2xl text-gray-600">
          Upload your resume and get an instant ATS score, detailed feedback,
          skill gap analysis, job matches, and AI interview practice — all for free.
        </p>

        <div className="mt-8 flex gap-4">
          <button className="px-6 py-3 bg-[#1FC8A9] text-white rounded-lg text-lg">
            Check ATS Score
          </button>
          <button className="px-6 py-3 border border-[#1FC8A9] text-[#1FC8A9] rounded-lg text-lg">
            Practice Interview
          </button>
        </div>
      </section>

      {/* Features */}
      <section className="px-8 py-16 bg-white">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 rounded-xl shadow">
            <h3 className="text-xl font-semibold text-[#0A2540]">
              ATS Score Analysis
            </h3>
            <p className="mt-2 text-gray-600">
              Get a resume score based on ATS rules and keyword matching.
            </p>
          </div>

          <div className="p-6 rounded-xl shadow">
            <h3 className="text-xl font-semibold text-[#0A2540]">
              Skill Gap Detection
            </h3>
            <p className="mt-2 text-gray-600">
              Identify missing skills and get course recommendations.
            </p>
          </div>

          <div className="p-6 rounded-xl shadow">
            <h3 className="text-xl font-semibold text-[#0A2540]">
              AI Interview Practice
            </h3>
            <p className="mt-2 text-gray-600">
              Practice HR and technical interviews with AI feedback.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-500">
        © {new Date().getFullYear()} ResumeIQ · Built for India 🇮🇳
      </footer>
    </main>
  );
}
