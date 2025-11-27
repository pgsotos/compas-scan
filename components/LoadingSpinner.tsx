export default function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 sm:py-12">
      <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-primary-600 mb-4"></div>
      <p className="text-gray-600 text-base sm:text-lg text-center px-4">{message}</p>
    </div>
  );
}
