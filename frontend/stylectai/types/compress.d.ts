declare module 'compress.js' {
  class Compress {
    compress(file: File, options: {
      quality: number;
      crop?: boolean;
      maxWidth?: number;
      maxHeight?: number;
    }): Promise<Array<{
      prefix: string;
      data: string;
      ext: string;
    }>>;
  }
  export default Compress;
} 